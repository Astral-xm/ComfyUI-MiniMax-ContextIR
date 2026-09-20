"""MiniMax H3 face reference-video preparation, ai-toolkit compatible.

Clean-room implementation written from the published behaviour of the
ComfyUI-AIToolkit-MiniMaxH3 reference-video node. That package ships no
licence file, so this file deliberately contains no code from it: it only
follows the documented preprocessing contract used by ai-toolkit's
``minimax_h3_ref2va`` sampling.

The node turns any VIDEO into the pieces ``MiniMaxH3ReferenceToVideo``
expects: 24 fps frames, a time-matched soundtrack, and the canvas size the
model should generate.
"""

from __future__ import annotations

import logging
import math

import torch
import torch.nn.functional as F

from comfy_api.latest import io


LOGGER = logging.getLogger("MiniMaxH3.FaceRefVideo")

H3_FPS = 24
FRAME_GRID_STEP = 17
FRAME_GRID_OFFSET = 5
CANVAS_ALIGN = 32
AUDIO_SAMPLE_RATE = 32000
_IMAGE_DTYPES = (torch.uint8, torch.float16, torch.bfloat16, torch.float32)


def _round_int(value: float) -> int:
    """Match the reference recipe's Python round() behaviour."""
    return int(round(float(value)))


def _finite_float(value, name: str, minimum: float | None = None) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite, got {value!r}")
    if minimum is not None and number < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value!r}")
    return number


def _snap_to_h3_grid(count: int) -> int:
    """Largest 17n+5 value not exceeding `count` (minimum 5)."""
    count = max(FRAME_GRID_OFFSET, int(count))
    return ((count - FRAME_GRID_OFFSET) // FRAME_GRID_STEP) * FRAME_GRID_STEP + FRAME_GRID_OFFSET


def _align_canvas(value: float) -> int:
    """Round to the nearest /32 pixel, never below one canvas block."""
    return max(CANVAS_ALIGN, _round_int(value / CANVAS_ALIGN) * CANVAS_ALIGN)


def _validate_frames(frames) -> torch.Tensor:
    if not torch.is_tensor(frames):
        raise TypeError(f"VIDEO components returned {type(frames).__name__}, expected a tensor")
    if frames.ndim != 4:
        raise ValueError(f"VIDEO frames must be [T, H, W, C], got {tuple(frames.shape)}")
    if frames.shape[-1] not in (1, 3, 4):
        raise ValueError(f"VIDEO frames need 1/3/4 channels, got {frames.shape[-1]}")
    if frames.dtype not in _IMAGE_DTYPES:
        raise TypeError(f"VIDEO frames need uint8/float16/bfloat16/float32, got {frames.dtype}")
    return frames


def _unit_frames(chunk: torch.Tensor) -> torch.Tensor:
    """Convert one frame chunk to RGB float in [0, 1]."""
    if chunk.dtype == torch.uint8:
        chunk = chunk.float() / 255.0
    else:
        chunk = chunk.float()
        if chunk.numel() and float(chunk.max()) > 1.5:
            chunk = chunk / 255.0
    channels = chunk.shape[-1]
    if channels == 1:
        chunk = chunk.repeat(1, 1, 1, 3)
    elif channels == 4:
        chunk = chunk[..., :3] * chunk[..., 3:4]
    return chunk.clamp_(0.0, 1.0)


def _target_canvas(height: int, width: int, target_megapixels) -> tuple[int, int]:
    if height <= 0 or width <= 0:
        raise ValueError(f"VIDEO frames have invalid size {width}x{height}")
    area = _finite_float(target_megapixels, "target_megapixels", 0.0) * 1_000_000.0
    scale = math.sqrt(area / (width * height))
    return _align_canvas(width * scale), _align_canvas(height * scale)


def _frame_chunk_size(height: int, width: int) -> int:
    # Keep one working chunk around 256 MB at float32 RGB or less, so 4K
    # references do not materialise a second full-resolution copy.
    return max(1, min(16, 64_000_000 // max(1, height * width)))


def _materialize_frames(source: torch.Tensor, picks: torch.Tensor,
                        out_height: int, out_width: int) -> torch.Tensor:
    total = int(picks.numel())
    source_h, source_w = int(source.shape[1]), int(source.shape[2])
    output = torch.empty((total, out_height, out_width, 3),
                         dtype=torch.float32, device=source.device)
    resize = (out_height, out_width) != (source_h, source_w)
    chunk_size = _frame_chunk_size(source_h, source_w)
    for start in range(0, total, chunk_size):
        stop = min(total, start + chunk_size)
        index = picks[start:stop].to(source.device)
        chunk = _unit_frames(source.index_select(0, index))
        if resize:
            chunk = F.interpolate(
                chunk.permute(0, 3, 1, 2),
                size=(out_height, out_width),
                mode="bicubic",
                antialias=True,
                align_corners=False,
            ).permute(0, 2, 3, 1)
        output[start:stop].copy_(chunk.clamp(0.0, 1.0))
        del chunk
    return output


def _frame_indices(frame_count: int, source_fps: float, output_frames: int) -> torch.Tensor:
    """Pick source frames on a real-time 24 fps grid, clamping the tail."""
    if source_fps <= 0:
        raise ValueError(f"VIDEO frame rate must be positive, got {source_fps}")
    last = frame_count - 1
    picks = []
    for i in range(output_frames):
        source = _round_int(i * source_fps / H3_FPS)
        picks.append(min(source, last))
    return torch.tensor(picks, dtype=torch.long)


def _resample_audio(waveform: torch.Tensor, source_rate: int, target_rate: int) -> torch.Tensor:
    if source_rate == target_rate:
        return waveform
    try:
        import torchaudio
        return torchaudio.functional.resample(waveform, source_rate, target_rate)
    except Exception:  # noqa: BLE001 - keep working without torchaudio
        length = max(1, _round_int(waveform.shape[-1] * target_rate / source_rate))
        return F.interpolate(waveform, size=length, mode="linear", align_corners=False)


def _stereo_float_waveform(waveform) -> torch.Tensor | None:
    if not torch.is_tensor(waveform) or waveform.numel() == 0:
        return None
    if waveform.ndim == 1:
        waveform = waveform[None, None, :]
    elif waveform.ndim == 2:
        waveform = waveform[None, :, :]
    elif waveform.ndim != 3:
        raise ValueError(f"AUDIO waveform must be 1D/2D/3D, got {waveform.ndim}D")
    if not waveform.is_floating_point():
        info = torch.iinfo(waveform.dtype)
        waveform = waveform.float() / max(1, abs(info.min))
    else:
        waveform = waveform.float()
    channels = int(waveform.shape[1])
    if channels == 1:
        waveform = waveform.repeat(1, 2, 1)
    elif channels > 2:
        waveform = waveform.mean(dim=1, keepdim=True).repeat(1, 2, 1)
    return waveform


def _normalize_audio(audio, seconds: float):
    waveform = None
    source_rate = 0
    if isinstance(audio, dict):
        waveform = audio.get("waveform")
        source_rate = int(audio.get("sample_rate") or 0)
    waveform = _stereo_float_waveform(waveform)
    if waveform is not None and source_rate > 0:
        if source_rate != AUDIO_SAMPLE_RATE:
            waveform = _resample_audio(waveform, source_rate, AUDIO_SAMPLE_RATE)
        want = max(1, _round_int(seconds * AUDIO_SAMPLE_RATE))
        if waveform.shape[-1] < want:
            waveform = F.pad(waveform, (0, want - waveform.shape[-1]))
        else:
            waveform = waveform[..., :want]
        return {"waveform": waveform.contiguous(), "sample_rate": AUDIO_SAMPLE_RATE}
    # Keep the output type valid when the clip has no usable soundtrack.
    samples = max(1, _round_int(seconds * AUDIO_SAMPLE_RATE))
    return {
        "waveform": torch.zeros(1, 2, samples, dtype=torch.float32),
        "sample_rate": AUDIO_SAMPLE_RATE,
    }


class MiniMaxH3FaceRefVideo(io.ComfyNode):
    """Convert a VIDEO into ai-toolkit style ref2va inputs."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MiniMaxH3FaceRefVideo",
            display_name="MiniMax H3 Face Ref Video",
            category="MiniMax ContextIR",
            description=(
                "Resamples a reference VIDEO to 24 fps with real-time pacing, "
                "snaps the frame count to MiniMax H3's 17n+5 grid, trims the "
                "soundtrack to the same window, and sizes the canvas from the "
                "clip's own aspect at the requested pixel area on a /32 grid. "
                "Frames are normalised to RGB, audio to 32 kHz stereo. The Face "
                "name describes the typical input; the node itself performs "
                "generic ref2va reference-video preparation. Clean-room "
                "implementation of the ai-toolkit ref2va contract."
            ),
            inputs=[
                io.Video.Input(
                    "video",
                    tooltip="参考视频；任意源帧率，节点会按真实时间轴重采样到 24fps。",
                ),
                io.Float.Input(
                    "target_megapixels",
                    default=0.258,
                    min=0.01,
                    max=4.0,
                    step=0.001,
                    tooltip=(
                        "生成画面的像素面积。0.258MP ≈ 672×384（ai-toolkit res-512 档）；"
                        "约 0.59MP 对应 res-768。"
                    ),
                ),
                io.Int.Input(
                    "max_length",
                    default=0,
                    min=0,
                    max=3600,
                    step=1,
                    tooltip="24fps 帧数上限；0 表示使用整段参考视频。",
                ),
            ],
            outputs=[
                io.Image.Output("frames", tooltip="24fps RGB 参考帧，可直接接到 ref_video_1。"),
                io.Audio.Output(
                    "audio",
                    tooltip="裁到与保留帧同时间窗、32kHz 立体声；无音轨时输出静音占位。",
                ),
                io.Int.Output("width", tooltip="生成宽度，按参考视频自身比例和 /32 对齐。"),
                io.Int.Output("height", tooltip="生成高度，按参考视频自身比例和 /32 对齐。"),
                io.Int.Output("length", tooltip="保留的 24fps 帧数（17n+5）。"),
            ],
        )

    @classmethod
    def execute(cls, video, target_megapixels, max_length=0) -> io.NodeOutput:
        components = video.get_components()
        source = _validate_frames(components.images)
        source_frames = int(source.shape[0])
        if source_frames < 1:
            raise ValueError("VIDEO contains no decodable frames")
        source_fps = _finite_float(components.frame_rate, "VIDEO frame rate", 0.0)
        if source_fps <= 0:
            raise ValueError(f"VIDEO frame rate must be positive, got {source_fps}")

        requested = int(source_frames / source_fps * H3_FPS)
        if max_length and max_length > 0:
            requested = min(requested, int(max_length))
        output_frames = _snap_to_h3_grid(requested)
        if requested < FRAME_GRID_OFFSET:
            LOGGER.warning(
                "Face Ref Video: %.2fs of source yields only %d frames at 24fps; "
                "repeating the last frame to reach the 5-frame minimum.",
                source_frames / source_fps,
                requested,
            )

        picks = _frame_indices(source_frames, source_fps, output_frames)
        out_width, out_height = _target_canvas(
            int(source.shape[1]), int(source.shape[2]), target_megapixels)
        frames = _materialize_frames(source, picks, out_height, out_width)

        seconds = output_frames / H3_FPS
        audio = _normalize_audio(getattr(components, "audio", None), seconds)

        LOGGER.info(
            "Face Ref Video: %d frames @ %gfps -> %d frames @24fps, canvas %dx%d",
            source_frames, source_fps, output_frames, out_width, out_height,
        )
        return io.NodeOutput(frames, audio, out_width, out_height, output_frames)
