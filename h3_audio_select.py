"""MiniMax H3 Audio Select - choose source or generated audio after sampling.

The node is the post-sampling counterpart of ``MiniMax H3 Unified to Video``:

- ``lock``            -> output ``source_audio`` (the exact waveform locked into
                          the AV latent; no VAE round-trip).
- ``remix`` / ``unlock`` -> output ``generated_audio`` (the sampler output decoded
                          by VAEDecodeAudio).

Keeping the selection after the sampler avoids the dependency cycle

    Audio Lock -> VAEDecodeAudio -> SamplerCustomAdvanced -> Audio Lock
"""

from __future__ import annotations

from comfy_api.latest import ComfyExtension, io


AUDIO_MODES = ["lock", "remix", "unlock"]


class MiniMaxH3AudioSelect(io.ComfyNode):
    """Pick the final audio after sampling."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="MiniMaxH3AudioSelect",
            display_name="MiniMax H3 Audio Select",
            description=(
                "Pick the final audio after sampling: lock -> source_audio, "
                "remix/unlock -> generated_audio (VAE decoded). Link audio_mode "
                "from MiniMax H3 Unified to Video to keep both nodes in sync."
            ),
            category="model/conditioning/minimax/unified",
            inputs=[
                io.Audio.Input(
                    "source_audio",
                    optional=True,
                    tooltip="Unified to Video 的“源音频”输出；lock 模式输出它（无损原音）。",
                ),
                io.Audio.Input(
                    "generated_audio",
                    optional=True,
                    tooltip="VAE 解码（音频）的输出；remix / unlock 模式输出它。",
                ),
                io.Combo.Input(
                    "audio_mode",
                    options=AUDIO_MODES,
                    default="lock",
                    optional=True,
                    tooltip=(
                        "可直接接 Unified to Video 的 audio_mode 输出。"
                        "lock 输出源音频；remix / unlock 输出生成音频。"
                    ),
                ),
            ],
            outputs=[io.Audio.Output(display_name="audio")],
        )

    @classmethod
    def execute(cls, source_audio=None, generated_audio=None, audio_mode="lock") -> io.NodeOutput:
        mode = str(audio_mode or "lock").strip().lower()
        if mode not in AUDIO_MODES:
            raise ValueError(f"audio_mode must be lock/remix/unlock, got {audio_mode!r}")
        if mode == "lock":
            if source_audio is None:
                raise ValueError(
                    "audio_mode=lock needs source_audio; connect Unified to Video's 源音频 output "
                    "or switch audio_mode to remix/unlock."
                )
            return io.NodeOutput(source_audio)
        if generated_audio is None:
            raise ValueError(
                f"audio_mode={mode} needs generated_audio; connect VAEDecodeAudio's AUDIO output "
                "or switch audio_mode to lock."
            )
        return io.NodeOutput(generated_audio)


class MiniMaxH3AudioSelectExtension(ComfyExtension):
    async def get_node_list(self):
        return [MiniMaxH3AudioSelect]


async def comfy_entrypoint():
    return MiniMaxH3AudioSelectExtension()


__all__ = [
    "MiniMaxH3AudioSelect",
    "MiniMaxH3AudioSelectExtension",
    "comfy_entrypoint",
]
