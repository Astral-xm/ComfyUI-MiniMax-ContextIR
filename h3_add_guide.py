"""Port of ComfyUI's MiniMax H3 Add Guide for the ContextIR pack.

Keeps the official behaviour (arbitrary frame index, multi-frame guide clips,
audio guides, chainable conditioning) while using this plugin's shared media
helpers. ComfyUI itself is GPL-3.0; see NOTICE for attribution.
"""

from __future__ import annotations

import math

import node_helpers
import torch
from comfy.ldm.minimax.model import FRAME_PER_TOKEN, FRAME_RESCALE
from comfy_api.latest import io

from .h3_unified import _encode_reference_audio, resize_image


class MiniMaxH3ContextIRAddGuide(io.ComfyNode):
    """Anchor an image, clip, audio, or clip+audio at an arbitrary frame."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MiniMaxH3ContextIRAddGuide",
            display_name="MiniMax H3 Add Guide (ContextIR)",
            category="model/conditioning/minimax/unified",
            description=(
                "Anchor an image, a short clip, audio, or a clip with its soundtrack "
                "at any frame of a MiniMax H3 video. Chain several nodes to anchor "
                "multiple frames."
            ),
            inputs=[
                io.Conditioning.Input("positive"),
                io.Vae.Input("vae", optional=True,
                             tooltip="Video VAE, needed when an image is connected."),
                io.Vae.Input("audio_vae", optional=True,
                             tooltip="Audio VAE, needed when audio is connected."),
                io.Latent.Input("latent"),
                io.Image.Input("image", optional=True,
                               tooltip="Image or clip to anchor. Multi-frame batches are cropped down to 5, 22, 39... (17n+5) frames; batches under 5 frames use the first image."),
                io.Audio.Input("audio", optional=True,
                               tooltip="Soundtrack anchored at the same frame index and cropped to the video's remaining duration."),
                io.Int.Input("frame_idx", default=0, min=-9999, max=9999,
                             tooltip="Anchor frame. Negative values count from the end of the video."),
            ],
            outputs=[io.Conditioning.Output(display_name="positive")],
        )

    @classmethod
    def execute(cls, positive, latent, frame_idx, vae=None, audio_vae=None,
                image=None, audio=None) -> io.NodeOutput:
        samples = latent["samples"]
        if (not getattr(samples, "is_nested", False)
                or len(samples.tensors) != 2
                or samples.tensors[0].ndim != 5
                or samples.tensors[0].shape[1] != 24):
            raise ValueError("MiniMaxH3ContextIRAddGuide expects a MiniMax H3 AV latent")
        if image is None and audio is None:
            raise ValueError("MiniMaxH3ContextIRAddGuide needs an image or audio to anchor")

        video = samples.tensors[0]
        height = video.shape[3] * 16
        width = video.shape[4] * 16
        frame_count = sum(FRAME_PER_TOKEN[k % 5] for k in range(video.shape[2]))

        guide_frames = 1
        if image is not None:
            if vae is None:
                raise ValueError("anchoring guide frames needs the vae input")
            guide_frames = int(image.shape[0])
            if guide_frames < 5:
                guide_frames = 1
            else:
                while guide_frames % 17 != 5:
                    guide_frames -= 1

        resolved = int(frame_idx)
        if resolved < 0:
            resolved = frame_count + resolved
        if resolved < 0 or resolved + guide_frames > frame_count:
            if guide_frames == 1:
                raise ValueError(f"frame_idx {frame_idx} is outside the video's {frame_count} frames")
            raise ValueError(
                f"a {guide_frames} frame guide clip at frame_idx {frame_idx} "
                f"does not fit in the video's {frame_count} frames")

        keyframe = {"resolved_frame_index": resolved}
        if image is not None:
            frames = resize_image(image[:guide_frames], width, height, "center")
            keyframe["latent"] = vae.encode(frames)

        if audio is not None:
            if audio_vae is None:
                raise ValueError("anchoring guide audio needs the audio_vae input")
            audio_latent, audio_rt = _encode_reference_audio(audio_vae, audio)
            max_rt = math.floor(samples.tensors[1].shape[-1] - FRAME_RESCALE * resolved)
            if max_rt < 1:
                raise ValueError(f"frame_idx {frame_idx} is past the end of the video's audio track")
            if audio_rt > max_rt:
                audio_latent = audio_latent[..., :max_rt].clone()
            keyframe["audio_latent"] = audio_latent

        keyframes = list(positive[0][1].get("minimax_keyframes", []))
        keyframes.append(keyframe)
        return io.NodeOutput(
            node_helpers.conditioning_set_values(positive, {"minimax_keyframes": keyframes}))

