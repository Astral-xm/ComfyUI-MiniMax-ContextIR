# 更新日志

## v2026.10.31

当前发布版本。

- Media Loader：提示词行改为多行 `textarea`，直接粘贴会保留换行；普通 Enter 换行，
  Ctrl/Command+Enter 保存。
- Tiled Sampler：新增独立的 **MiniMax H3 Tiled Sampler (Legacy)** 节点，
  node_id 为 `MiniMaxH3TiledSamplerLegacy`，保留旧版实现用于 A/B 对比；
  当前版本 `MiniMaxH3TiledSampler` 不受影响。
- Unified to Video：选中的源音频被 Media Loader 关闭或未连接时，
  `lock/remix` 自动降级为 `unlock`，不再中断工作流，并在 `report` 中注明。

## v2026.10.20

上一发布版本，保留用于回退。

- Media Loader：`image1` 关闭后不再占用图片编号，后续第一张启用图片自动成为
  `image1`；Reference Splitter 的实际输出同步前移，避免界面与下游标签错位。
- Media Loader：保留 `FirstFrame` / `LastFrame` 固定帧槽位，图片网格、视频行高、
  提示词与音频滚动区域按节点高度自适应。
- Reference Splitter：固定输出 11 张图片、3 个视频、3 个视频音轨、3 个音频、
  3 个提示词，并支持短边缩放、尺寸对齐、宽高比与时长输出。
- Unified to Video：合并音频锁定能力，增加源音频与 `audio_mode` 输出；
  新增 Audio Select 节点，支持 lock / remix / unlock 音频选择。
- 新增 Tiled Sampler、Face Ref Video、Sigma Refiner 等 H3 工作流节点。
- 新增 `h3-prompt-writing-CN`、`Singularity-h3-prompt-writing-CN` 与
  `Singularity-h3-prompt-writing-EN` 技能；原有通用技能显示名调整为 `-EN`。

## v2026.09.13

上一发布快照，保留用于回退。

- 包含当时已发布的基础 H3 条件构建、Media Loader、Reference Splitter、
  Resolution Selector 与多模态对话功能。
- 不包含 `v2026.10.20` 中的图片动态编号修复、音频锁定整合、分块采样器及新增技能。

## 回退方法

```bash
git fetch --tags
git checkout v2026.10.20
pip install -r requirements.txt
```

返回最新版：

```bash
git checkout main
git pull
pip install -r requirements.txt
```

切换版本后重启 ComfyUI；前端界面如未更新，按 `Ctrl + F5` 强制刷新。
