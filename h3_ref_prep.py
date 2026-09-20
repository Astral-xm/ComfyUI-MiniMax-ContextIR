"""MiniMax H3 reference-video preparation, ai-toolkit compatible.

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

import math

import torch
import torch.nn.functional as F

from comfy_api.latest import io


H3_FPS = 24
FRAME_GRID_STEP = 17
FRAME_GRID_OFFSET = 5
CANVAS_ALIGN = 32
SILENT_AUDIO_SAMPLE_RATE = 32000


def _nearest_int(value: float) -> int:
    """Round half away from zero, avoiding Python's banker's rounding."""
    return int(math.floor(value + 0.5)) if value >= 0 else -int(math.floor(-value + 0.5))


def _snap_to_h3_grid(count: int) -> int:
    """Largest 17n+5 value not exceeding `count` (minimum 5)."""
    count = max(FRAME_GRID_OFFSET, int(count))
    return ((count - FRAME_GRID_OFFSET) // FRAME_GRID_STEP) * FRAME_GRID_STEP + FRAME_GRID_OFFSET


def _align_canvas(value: float) -> int:
    """Round to the nearest /32 pixel, never below one canvas block."""
    return max(CANVAS_ALIGN, _nearest_int(value / CANVAS_ALIGN) * CANVAS_ALIGN)


def _as_image_batch(images) -> torch.Tensor:
    if not torch.is_tensor(images):
        raise TypeError(f"VIDEO components returned {type(images).__name__}, expected a tensor")
    if images.ndim != 4:
        raise ValueError(f"VIDEO frames must be [T, H, W, C], got {tuple(images.shape)}")
    if images.shape[-1] not in (1, 3, 4):
        raise ValueError(f"VIDEO frames need 1/3/4 channels, got {images.shape[-1]}")
    images = images.float()
    if images.is_floating_point() and images.numel() and float(images.max()) > 1.5:
        images = images / 255.0
    return images


def _frame_indices(frame_count: int, source_fps: float, output_frames: int) -> torch.Tensor:
    """Pick source frames on a real-time 24 fps grid, clamping the tail."""
    if source_fps <= 0:
        raise ValueError(f"VIDEO frame rate must be positive, got {source_fps}")
    last = frame_count - 1
    picks = []
    for i in range(output_frames):
        source = _nearest_int(i * source_fps / H3_FPS)
        picks.append(min(source, last))
    return torch.tensor(picks, dtype=torch.long)


def _trim_audio(audio, seconds: float, output_frames: int):
    waveform = None
    sample_rate = 0
    if isinstance(audio, dict):
        waveform = audio.get("waveform")
        sample_rate = int(audio.get("sample_rate") or 0)
    if torch.is_tensor(waveform) and waveform.numel() and sample_rate > 0:
        keep = max(0, _nearest_int(seconds * sample_rate))
        return {
            "waveform": waveform[..., :keep].contiguous(),
            "sample_rate": sample_rate,
        }
    # Keep the output type valid when the clip has no usable soundtrack.
    samples = max(1, _nearest_int(seconds * SILENT_AUDIO_SAMPLE_RATE))
    return {
        "waveform": torch.zeros(1, 2, samples, dtype=torch.float32),
        "sample_rate": SILENT_AUDIO_SAMPLE_RATE,
    }


def _fit_frames(frames: torch.Tensor, target_megapixels: float) -> tuple[torch.Tensor, int, int]:
    height, width = int(frames.shape[1]), int(frames.shape[2])
    if height <= 0 or width <= 0:
        raise ValueError(f"VIDEO frames have invalid size {width}x{height}")
    area = float(target_megapixels) * 1_000_000.0
    scale = math.sqrt(area / (width * height))
    out_width = _align_canvas(width * scale)
    out_height = _align_canvas(height * scale)
    if (out_height, out_width) != (height, width):
        frames = F.interpolate(
            frames.permute(0, 3, 1, 2),
            size=(out_height, out_width),
            mode="bicubic",
            antialias=True,
            align_corners=False,
        )
        frames = frames.clamp_(0.0, 1.0).permute(0, 2, 3, 1).contiguous()
    return frames, out_width, out_height


class MiniMaxH3AIToolkitRefVideo(io.ComfyNode):
    """Convert a VIDEO into ai-toolkit style ref2va inputs."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MiniMaxH3AIToolkitRefVideo",
            display_name="MiniMax H3 Face Ref Video",
            category="MiniMax ContextIR",
            description=(
                "Resamples a reference VIDEO to 24 fps with real-time pacing, "
                "snaps the frame count to MiniMax H3's 17n+5 grid, trims the "
                "soundtrack to the same window, and sizes the canvas from the "
                "clip's own aspect at the requested pixel area on a /32 grid. "
                "Clean-room implementation of the ai-toolkit ref2va contract."
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
                io.Image.Output("frames", tooltip="24fps 参考帧，可直接接到 ref_video_1。"),
                io.Audio.Output("audio", tooltip="与保留帧同时间窗的音轨；无音轨时输出静音占位。"),
                io.Int.Output("width", tooltip="生成宽度，按参考视频自身比例和 /32 对齐。"),
                io.Int.Output("height", tooltip="生成高度，按参考视频自身比例和 /32 对齐。"),
                io.Int.Output("length", tooltip="保留的 24fps 帧数（17n+5）。"),
            ],
        )

    @classmethod
    def execute(cls, video, target_megapixels, max_length=0) -> io.NodeOutput:
        components = video.get_components()
        frames = _as_image_batch(components.images)
        source_frames = int(frames.shape[0])
        source_fps = float(components.frame_rate)
        if source_frames < 1:
            raise ValueError("VIDEO contains no decodable frames")

        output_frames = int(source_frames / source_fps * H3_FPS)
        if max_length and max_length > 0:
            output_frames = min(output_frames, int(max_length))
        output_frames = _snap_to_h3_grid(output_frames)

        picks = _frame_indices(source_frames, source_fps, output_frames)
        frames = frames.index_select(0, picks)
        frames, out_width, out_height = _fit_frames(frames, float(target_megapixels))

        seconds = output_frames / H3_FPS
        audio = _trim_audio(getattr(components, "audio", None), seconds, output_frames)

        print(
            f"[MiniMaxH3 ref-prep] {source_frames} frames @ {source_fps:g}fps -> "
            f"{output_frames} frames @24fps, canvas {out_width}x{out_height}"
        )
        return io.NodeOutput(frames, audio, out_width, out_height, output_frames)
