
## 使用教程

（B 站）：https://space.bilibili.com/176339505

# ComfyUI-MiniMax-ContextIR

MiniMax H3 视频生成全家桶：一个 ComfyUI 插件，十一个节点，覆盖
“提示词优化 → 素材加载 → 条件构建 → 音频锁定 → 采样输出”的完整 H3 工作流。
既可直接配合官方 MiniMax H3 本地模型（FLOW_AV / fl2va）使用，也可调用
H3-Context-IR 云端 API 自动把普通提示词优化成结构化 H3 提示词。

## 功能总览

- **MiniMax H3 Unified to Video**：本地 H3 Conditioning（融合官方 Image to Video /
  Reference to Video，支持 t2va / i2va / fl2va / l2va / ref2va / hybrid，自动识别任务类型）。
- **MiniMax H3 Context IR**：独立调用 H3-Context-IR API，把普通提示词 + 媒体优化成
  结构化 H3 提示词（t2va / i2va / r2va），输出字符串。
- **MiniMax H3 Multimodal Chat**：多轮对话节点，可加载内置的 MiniMax 官方 Skill、调用任意
  OpenAI 兼容多模态 LLM API、通过 @ 引用 H3 媒体输入，并支持自动化外部文本输入。
- **音频锁定（内置于 MiniMax H3 Unified to Video）**：`source_audio` 可选
  `video_audio_1..3` / `audio_1..3`，采样前把源音频锁进 AV latent，并把无损原音
  从新增的“源音频”输出送出——对口型 / 音乐 MV 场景必备。
- **MiniMax H3 Audio Select**：采样后音频选择器，按 `audio_mode` 在 Unified 的
  “源音频”（lock，无损原音）与 VAE 解码的生成音频（remix / unlock）之间自动切换。
- **Media Loader**：参考 Fantastic MiniMaxH3 PromptBuilder 并修改优化的
  媒体加载器（拖拽上传、预览、排序、音轨拆分、裁剪/抽帧、中英双语界面、预设），
  输出 `references` 素材包。
- **Reference Splitter**：把 `references` 素材包拆成固定的 11 图 / 3 视频 /
  3 视频音轨 / 3 音频 / 3 提示词字符串槽位（空槽位为 None）。
  内置 `short_edge_max` / `align_to` 两个 INT 输入用于全局图片缩放
  （短边 ≤ short_edge_max，尺寸对齐到 align_to 的倍数）。
- **MiniMax H3 Resolution Selector**：宽高比 + 官方“宽×高”预设 → H3 宽高；
  切换比例时“宽×高”选项自动跟随（原生 DynamicCombo）。
- **MiniMax H3 Concat AV Latent**：把独立的视频/音频 latent 合并成 H3 采样器所需的
  联合 NestedTensor AV latent（参考 PT_H3ConcatAVLatent，主要用于视频的二次采样放大）。
- **MiniMax H3 Tiled Sampler**：替代 SamplerCustomAdvanced 的分块采样器；把 AV latent
  沿 H/W 轴切条逐条采样，R2V 参考条件按条同步裁切（修复拼接重复），关键帧按区域
  裁切，音轨完整透传，接缝带二次精修；支持 MultiDiffusion/independent 融合、
  cosine/gaussian 融合窗口、R2V 参考透传/裁切/整图回退、全局草稿阶段和 mask 裁切；
- **MiniMax H3 Face Ref Video**：把任意帧率的参考视频整理成 ai-toolkit
  ref2va 口径的 24fps 帧、17n+5 帧数、同步音轨与 /32 对齐的生成宽高；
- **MiniMax H3 Sigma Refiner**：低噪细节精修器；在低 Sigma 区间局部加步，消除高速
  运动边缘的马赛克与像素紊乱，插在调度器和采样器之间使用；

## 特性

- 全部使用 ComfyUI 新版 `ComfyExtension` / V3 io API 注册，与官方及其他 H3 插件可共存；
- 提示词自动规范化媒体标签 `<Picture i>` / `<Video k>` / `<Audio j>`，
  引用未连接的媒体会给出明确警告而不是静默失败；
- 时长自动按官方 17n+5 帧网格对齐：`max(5, round(duration*fps)) + (5 - ... % 17) % 17`；
- 媒体加载器全界面中/英双语可切换；聊天节点支持 @ 媒体引用、多历史对话管理、
  Skill 首轮注入（远端 API 无需访问本地文件）。

## 兼容性

- ComfyUI ≥ 0.31（新式 `ComfyExtension`；不支持旧式 `NODE_CLASS_MAPPINGS` 注册方式）
- MiniMax H3 官方模型：UNET + Qwen3-VL CLIP + 视频 VAE + 音频 VAE
- Python 3.10+；媒体加载器需要 PyAV 或 ffmpeg 之一（音频解码可回退 ComfyUI LoadAudio）
- `requirements.txt` 默认只安装 PyAV；`opencv-python-headless`、`imageio` 和
  `imageio-ffmpeg` 都是可选回退依赖，使用 PyAV 或系统 ffmpeg 时无需安装。

## 安装

### 方式一：git clone（推荐）

```bash
git clone https://github.com/oufeixinxinren/ComfyUI-MiniMax-ContextIR.git
cd ComfyUI-MiniMax-ContextIR
pip install -r requirements.txt
```

把克隆出的 `ComfyUI-MiniMax-ContextIR` 文件夹放进 `ComfyUI/custom_nodes/`。

### 方式二：手动复制

把整个项目文件夹复制到 `ComfyUI/custom_nodes/`，然后执行：

```bash
pip install -r requirements.txt
```

安装后**重启 ComfyUI**。节点分类：

- `model/conditioning/minimax/unified`：Unified / Concat AV Latent /
  Resolution Selector 等
- `MiniMax ContextIR`：Context IR
- `MiniMaxH3 Media/Fant`：Media Loader / Reference Splitter

## 快速开始

1. 用 **Media Loader** 上传参考图/视频/音频，点击 **刷新输出拆分器**
   创建 Reference Splitter；改动素材后再点一次即可刷新其槽位；
2. 接入 **Unified to Video**（`mode=auto` 按已连接输入自动判断任务类型），填写提示词；
3. `positive` → BasicGuider；`av_latent` → SamplerCustomAdvanced（需要锁音时在
   Unified 里选 `source_audio`，latent 会自动带音频 mask）；
4. 采样结果 → VAEDecode；音轨用 Unified 的“源音频”输出（lock，无损原音）或
   VAEDecodeAudio（remix/unlock/off，生成音频）保存；需要二次放大采样时用
   Concat AV Latent 把重编码的视频/音频 latent 再喂给采样器；
5. 需要提示词优化时，用 **Multimodal Chat** 或 **Context IR** 节点生成结构化 H3 提示词。

---

## 节点 1：MiniMax H3 Unified to Video
<img width="351" height="664" alt="image" src="https://github.com/user-attachments/assets/d9b67219-f43b-4620-8e8d-f7641dbacd63" />

本地 H3 条件构建，`mode=auto` 时按已连接输入自动判断：

| 已连接输入 | 自动任务 |
| --- | --- |
| 无 | t2va |
| 仅首帧 | i2va |
| 首帧 + 末帧 | fl2va |
| 仅末帧 | l2va |
| 参考媒体（图/视频/音频） | ref2va |
| 关键帧 + 参考媒体 | hybrid |

### 输入

| 输入 | 说明 |
| --- | --- |
| `clip` | MiniMax H3 Qwen3-VL CLIP |
| `video_vae` | 可选；关键帧和 DiT 参考块需要。不接时参考媒体仍会进入文本编码器 |
| `audio_vae` | 可选；参考视频音轨/参考音频时需要 |
| `prompt` | 输入提示词（用 `<Picture i>` / `<Video k>` / `<Audio j>` 引用已连接媒体） |
| `mode` | auto / t2va / fl2va / ref2va |
| `width` / `height` | 本地画布（32 倍数，单边上限 16384；与官方节点一致，不再额外限制 2MP 面积） |
| `duration` | 场景时长（秒，1–30，浮点；2–15 是训练范围，15–30 未测试） |
| `length_override` | 0 = 使用 duration/fps；>0 = 直接使用官方 raw 帧数并向上吸附到 17n+5 |
| `fps` | 帧率（1–60，默认 24），仅用于时长 → 帧数换算 |
| `ref_image_size` | 本地参考图缩放：match / max |
| `first_frame` / `last_frame` | 关键帧 |
| `ref_images` / `ref_videos` / `ref_video_audios` / `ref_audios` | 参考媒体（接满自动出现下一路） |
| `source_audio` | **源音频**：`off` / `video_audio_1..3` / `audio_1..3`，从已连接的音轨中选择锁定源 |
| `audio_mode` | `lock`（音频 denoise=0，完全保持原音）/ `remix`（按强度重绘）/ `unlock`（不改 latent，也不校验 `source_audio` 是否已连接） |
| `audio_strength` | remix 模式的音频降噪强度（0–1；lock/unlock 忽略） |

### 输出

- `positive`：CONDITIONING，接 BasicGuider
- `av_latent`：联合视频+音频 latent，接 SamplerCustomAdvanced.latent_image
- `conditioned_prompt`：规范化媒体标签后的提示词
- `media_map_json`：媒体编号与来源映射
- `report`：本地任务、帧数、媒体数量、音频锁定等诊断信息
- `源音频`：所选 `source_audio` 的原始波形（无损；未选择时为空），lock 模式直接保存它
- `audio_mode`：当前生效的音频模式（`lock` / `remix` / `unlock`），可直接接
  **MiniMax H3 Audio Select** 的 `audio_mode` 输入，保证两个节点模式一致

### 注意

- 参考视频建议 48–720 帧（2–30 秒，24fps）；2–15 秒是训练范围，15–30 秒属于未测试区间。
- 帧数按官方公式自动计算并对齐到 17n+5：
  `max(5, round(duration*fps)) + (5 - (max(5, round(duration*fps)) % 17)) % 17`。
- 显式模式会屏蔽（忽略）不属于该模式的输入，而不是报错；只有缺失必需输入才报错：
  - `mode=t2va`：忽略全部已连接媒体；
  - `mode=fl2va`：忽略参考媒体，按已连接关键帧自动映射（仅首帧 → i2va，
    仅末帧 → l2va，首尾帧都有 → fl2va；无任何关键帧 → 报错）。
- `mode=ref2va` 时首尾帧与参考媒体可同时输入（内部按 hybrid 处理）；
  未接任何参考媒体 → 报错。
- 音频锁定内置于 Unified：`source_audio` 选择源音频（video_audio_1..3 / audio_1..3），
  `audio_mode` 为 lock / remix / unlock；lock 时用 Unified 的“源音频”输出保存无损原音。
- 参考媒体在没有 `video_vae` / `audio_vae` 时仍会作为文本编码器条件；
  参考视频的音轨在 token 呈现顺序中按官方规则排在视频前面。

### 官方更新合并情况

已合并的非冲突更新：

- `length_override`：支持官方 raw 帧数（5–3600，自动吸附 17n+5）
- `video_vae` / `audio_vae` 可选：支持无 VAE 的纯文本参考条件
- 参考视频音轨按官方顺序 `audio → video` 进入文本编码器
- 修复参考视频无音轨时不进入文本编码器的问题
- 官方 **Add Guide for MiniMax H3** 可直接接在 Unified 的 `positive` + `av_latent`
  后面使用，不需要本插件再复制一个同功能节点
- 参考视频的 `adapt_canvas` 上限已对齐官方 `768×1344` 面积
- 去掉了 Unified 之前额外的 1920×1088 生成画布硬上限

保留的冲突项（未按官方结构改写）：

- 官方现在用 Image to Video / Reference to Video 两个节点 + AddGuide 组合；
  本插件继续保留单节点 Unified 的 hybrid 结构，AddGuide 仍使用官方节点
- Unified 仍保留 duration/fps 输入，默认范围已扩到 1–30 秒；raw length 只是额外入口
- 官方 Fun ControlNet、Empty AV Latent、ModelSamplingMiniMaxH3 不并入 Unified；
  这些官方节点可直接与本插件共存使用

---

## 节点 2：MiniMax H3 Context IR
<img width="302" height="451" alt="image" src="https://github.com/user-attachments/assets/4bb37e09-5cb9-49d8-8d16-de73679b8a55" />

独立调用 H3-Context-IR API：输入普通提示词（+ 关键帧或参考媒体），返回优化后的
结构化 H3 提示词字符串。

### 输入

| 输入 | 说明 |
| --- | --- |
| `mode` | t2va（纯文本）/ i2va（首尾帧）/ r2va（参考媒体，需至少一路） |
| `text` | 原始提示词 |
| `duration` | 浮点，1–15 秒（自动钳制并四舍五入） |
| `ratio` | adaptive / 21:9 / 16:9 / 4:3 / 1:1 / 3:4 / 9:16（t2va 不能 adaptive） |
| `first_frame` / `last_frame` | 关键帧（i2va） |
| `ref_images` / `ref_videos` / `ref_video_audios` / `ref_audios` | 参考媒体（r2va；与 Unified 节点相同，每个类别先显示一路，接入后自动增加下一路） |
| `api_key` / `base_url` / `callback_url` | API 配置（key 必填或设 `MINIMAX_API_KEY`） |

### 输出

- `enhanced_prompt`：优化后的 H3 提示词字符串

### 注意

- 在 https://www.minimaxi.com/ 注册登录后获取 API Key；可通过节点内 `api_key`
  输入框或环境变量 `MINIMAX_API_KEY` 设置。
- 会阻塞到 API 任务完成（最长 180 秒），失败直接抛错。
- r2va 与首尾帧在官方 API 中互斥：r2va 只能带参考媒体，关键帧请用 i2va。

---

## 节点 3：MiniMax H3 Multimodal Chat
<img width="597" height="1104" alt="image" src="https://github.com/user-attachments/assets/0ec801ef-15e2-407e-b3af-521780a21212" />

多轮对话节点，支持 Skill 加载与外部多模态 API：

- **Skill 加载**：直接在节点的 `skill` 下拉框选择即可生效（自动发现本插件 `skills/`
  下内置的 MiniMax 官方 Skill，含 `h3-prompt-writing`；
  `skill=auto` 时由外部 LLM 根据首个任务自动选择）。选择后 Skill 内容会注入系统提示词，
  并启用阶段式执行协议：模型按阶段推进、可请求按需加载 references、
  通过 `<mmx_skill_state>` 状态标记返回阶段/选项/final。
- **外部多模态 API**：任意 OpenAI 兼容的 `/chat/completions` 接口
  （`api_base` + `api_key` + `model`）。
- **H3 媒体端口**：与 Unified 节点一致的首尾帧、参考图/视频/音频输入。
- **@ 引用**：节点接入素材后，对话框上方会出现可引用的媒体选项，点击后插入
  `@first_frame` / `@last_frame` / `@ref_image_N` / `@ref_video_N` /
  `@ref_video_audio_N` / `@ref_audio_N`；后端会把这些引用解析为
  `<Picture i>` / `<Video k>` / `<Audio j>` 标签并随 API 请求发送媒体内容
  （视频自动抽帧为图片）。
- **仅输出提示词**：`prompt_only` 开启时不调用 API，直接输出组装好的提示词文本。
- **多对话管理**：左侧“最近聊天”栏支持新建、切换、删除对话（上限 20 个），
  支持“清空全部”；**双击会话按钮可重命名**；对话列表随工作流保存，重启后仍可继续。
- **Skill 状态可见**：聊天区顶部显示当前 Skill 与阶段（流程条），
  首轮加载后显示“已加载”。

### 输入

| 输入 | 说明 |
| --- | --- |
| `prompt` | 用户消息（聊天窗口内填写，支持 @ 引用） |
| `input_string` | 外部文本输入端口；连接外部文本输出后优先作为消息输入（覆盖聊天窗口手输内容），方便自动化分段生成 |
| `user_prompt` | 提示词字符串端口（所有媒体端口之后）；连接的字符串自动加载到聊天对话框，且执行时直接作为用户消息（对话框有手输内容时优先）。节点被屏蔽（Bypass）时该内容直接透传到 `prompt_text` 输出 |
| `chat_history` / `request_id` | 由前端聊天窗口自动维护 |
| `skill` | auto 或具体 Skill |
| `prompt_mode` | 提示词生成模式：auto / T2VA / I2VA / FL2VA / L2VA / REF2VA；auto 时由模型根据已连接端口和需求自动判断；显式模式会屏蔽不属于该模式的媒体输入：T2VA 忽略全部媒体；I2VA / L2VA / FL2VA 忽略参考媒体（缺必需关键帧时报错）；REF2VA 允许首/尾关键帧与参考媒体并用（无任何参考媒体时报错） |
| `duration` | 目标视频时长（秒，1–30；2–15 为训练范围，15–30 未测试） |
| `api_base` / `api_key` / `model` | OpenAI 兼容 API 配置 |
| `temperature` | 采样温度 |
| `enable_thinking` / `reasoning_effort` | 是否请求模型思考（reasons），及思考强度（需模型/服务商支持） |
| `output_thinking` | 是否在回复中保留 `<think>` 思考块；关闭则自动清理 |
| `max_tokens` | 最大生成长度（0–128000，发送前自动钳制；实际还受模型限制） |
| `max_history_rounds` | 客户端历史裁剪轮数（默认 1000）；真正的限制是模型上下文窗口 |
| `auto_load_references` | 开关（默认开）；首轮加载 Skill 时自动把本地 reference 文件内容注入系统提示词，远端 API 无需访问本地文件 |
| `first_frame` / `last_frame` / `ref_images` / `ref_videos` / `ref_video_audios` / `ref_audios` | H3 媒体参考输入 |

### 输出

- `reply`：助手回复完整文本
- `prompt_text`：自动提取并清洗后的 H3 提示词（过滤“您需要的提示词如下：”等套话，
  优先取代码块内容）；空输入时复用上一条结果，不再调用 API
- `chat_history`：更新后的对话历史 JSON
- `report`：prompt_only 状态、媒体/引用数量、skill、阶段/选项/final、已加载 references、api_call 状态

### 注意

- Skill 只在首轮加载，后续轮次不重复上传；**切换 Skill 会重启对话**（清空历史后重新加载）。
- `input_string` 有文本时，节点一旦执行就会自动调用 API 并输出新的 `prompt_text`（无需点击发送，
  且每次运行都会调用，不会命中缓存）；`input_string` 为空时，只有点击发送（或运行前
  `prompt` 已有内容）才会发送，否则仅复用上一条输出。
- 点击清空后，下一次对话也会重新加载当前选择的 Skill。
- 新建对话会在第一条消息时重新加载当前 Skill；切换对话则沿用该对话已加载的 Skill 状态。
- 未连接的 @ 引用会直接报错。
- 外部 API 需支持 OpenAI 兼容的多模态消息格式（`image_url` / `input_audio`）。
- 上下文长度无法真正“无限制”：是否够长取决于所调用模型的上下文窗口；
  客户端默认不再主动截断（1000 轮上限），超出窗口时 API 会返回上下文超限错误。
- Skill 的 `references/` 是本地文件，远端 API 读不到；节点会在首轮把文件内容读出来
  注入系统提示词（`auto_load_references` 默认开启）。文件较多/较大时可关闭该开关，
  改由模型按需请求加载。

---

## 节点 4：音频锁定（内置于 MiniMax H3 Unified to Video）

H3 的 `ref_audio` 本质上只是“参考”：模型会按音色、节奏和内容**重新生成**一条音频，
提示词写得再明确（`fully_copy` / `audio reuse` 等）也无法保证原样输出。要让成片音频
就是接入的参考音频（比如对口型、音乐 MV），需要在采样前把源音频“锁”进 AV latent。

音频锁定已**合并进 Unified to Video**，由三个参数控制：

| 参数 | 说明 |
| --- | --- |
| `source_audio` | **源音频**：`off` / `video_audio_1..3` / `audio_1..3`；选中后把对应音轨锁进 latent |
| `audio_mode` | `lock`：音频 denoise=0（完全保持原音，只生成画面）；`remix`：按 `audio_strength` 重绘；`unlock`：不修改 latent，也不校验 `source_audio` 是否已连接 |
| `audio_strength` | remix 模式的音频降噪强度（0–1，lock/unlock 忽略） |

- 选中 `source_audio` 后，Unified 的 `av_latent` 输出即**已锁好音轨**的 latent（带音频 noise_mask），直接接采样器；
- Unified 新增 **“源音频”输出**：直接给出所选源音频的原始波形（未经 VAE 编解码，无损），保存 / 合成时用它；
- `source_audio=off` 或 `audio_mode=unlock` 时不修改 latent；`audio_mode=unlock` 时
  不校验 `source_audio` 是否真有音频输入（此时“源音频”输出为空）；
  `remix/unlock` 的最终音轨用 **VAE 解码（音频）** 的输出。

### 节点：MiniMax H3 Audio Select

采样后的音频选择器，用来在“无损源音频”和“生成音频”之间二选一：

| 输入 | 说明 |
| --- | --- |
| `source_audio` | 接 Unified to Video 的 **“源音频”** 输出（无损原音） |
| `generated_audio` | 接 **VAE 解码（音频）** 的 AUDIO 输出（采样器生成音轨） |
| `audio_mode` | `lock` / `remix` / `unlock`；可直接接 Unified 的 `audio_mode` 输出 |

| 模式 | 输出 |
| --- | --- |
| `lock` | `source_audio`（原始波形，不经过 VAE 编解码） |
| `remix` / `unlock` | `generated_audio`（VAE 解码后的生成音轨） |

> 建议把 Unified 的 `audio_mode` 输出接到 Audio Select 的 `audio_mode` 输入，
> 这样只改 Unified 一处即可同步两边的选择；不接时也可以手动选择模式。

### 用法

```
Unified to Video
  ├─ positive ──> BasicGuider / Sampler
  ├─ av_latent ──> SamplerCustomAdvanced.latent_image   (source_audio 选中时已锁定音轨)
  ├─ 源音频 ──> Audio Select.source_audio
  └─ audio_mode ──> Audio Select.audio_mode
采样结果 ──> VAEDecodeAudio ──> Audio Select.generated_audio
Audio Select.audio ──> 保存/合成（由模式自动选择源音频或生成音轨）
```

> 为什么放在 Unified 内部：锁定逻辑必须把 latent 送进采样器，而最终音轨又来自采样器
> 的解码结果；若用独立的锁定节点再接入解码音频，就会形成
> AudioLock → VAEDecodeAudio → Sampler → AudioLock 的依赖环。内置于条件节点后环自然消失。

---

## 节点 5/6：Media Loader + Reference Splitter
<img width="1177" height="698" alt="image" src="https://github.com/user-attachments/assets/861f4a47-c1d4-4c3e-9a4a-3cfa05723c8f" />

参考并重构自 [ComfyUI-Fantastic-MiniMaxH3-PromptBuilder](https://github.com/Adudeguyman/ComfyUI-Fantastic-MiniMaxH3-PromptBuilder)
的媒体加载器（MIT License，Copyright (c) 2026 Adudeguyman）。节点 id 为
`MiniMaxH3MediaLoaderFantastic`，在保留原版媒体加载核心能力的基础上进行了修改与优化：

- 拖拽 / 文件选择上传图片、视频、音频，缩略图与播放预览；
- 拖动素材直接交换顺序（无排序按钮）、启停、移除；视频音轨可“配对”或“独立”拆分；
- 缩略图显示像素尺寸与比例角标（16:9、4:3、9:16 …，近似值带 `≈`）；
- 裁剪 / 抽帧编辑器：不改原文件即可裁剪视频时长（`trim`）、拖拽裁剪框（`crop`），
  并可直接从视频抽出一帧作为图片参考；图片也有 ✂ 按钮，可按 1:1 / 4:3 / 3:2 /
  16:9 / 9:16 / 3:4 / 2:3 / 21:9 或自由比例裁剪；
- 音频剪辑：悬浮缩略图静音预览、打开播放带声音；输入结束时间后点 **＋ Segment**
  在波形上添加可点击的分段序号标记，单击即选中该分段（下一段起点默认接上一段终点），
  点 **－ Segment** 删除选中分段，点 **↳ Use segment** 将当前分段加载为新的
  音频素材（同一文件、仅选中分段时间）；分段随素材保存（Apply 后保留），
  点 **↺ Reset** 清空所有分段；
- 音轨标签：视频音轨（配对或独立）统一使用 `<V_Audio N>`，与独立音频素材
  `<Audio M>` 分属不同命名空间；“独立”模式下只发送视频内含的音轨
  （不发送视频画面），标签也只保留 `<V_Audio N>`；
- 面板顶部有 **中 / EN** 语言切换按钮，一键切换全界面中英文（含按钮、提示、
  裁剪弹窗），选择会保存在浏览器本地；
- 2–30s 片段与每类 30s 总量限制提示（前端；2–15s 为训练范围）；每类初始只显示一个 "+" 槽，
  点击或拖入即加载素材，删除素材后格子自动收回；图片槽为 1:1 正方形
  （3×3，每格约 1/9），超过 9 张后侧边滚动查看；上限 90 图 / 30 视频 / 90 音频；
- 媒体预设（presets）保存、加载、删除；
- 输出单路 `references`（H3_REFS 素材包）；点击面板上的 **刷新输出拆分器**
  按钮会创建并连接 **MiniMax H3 Reference Splitter**（再次点击按当前素材刷新
  槽位）。图片槽位：前三个格子固定为 **FirstFrame / LastFrame / image1** ——
  点哪个格子加载就把图片装进哪个格子（前面的格子空着也不会让后面的图片往前
  挤）；**image2 起是可顺延的队尾**，关闭或删除其中一个后，后面的格子会自动
  往前补。图片还可以**互相拖拽**：拖到已占用的格子上会与对方互换，拖到空的
  "+"格子上则直接移动进去（FirstFrame/LastFrame/image1 与 imageN 之间都能
  互拖）。视频/音频槽位按已启用的素材生成。之后再接入官方的 Reference to
  Video 或本插件的 Unified 节点。

本节点不包含原插件的 Prompt Builder / 提示词库；需要提示词编辑请安装原插件。

### HTTP 接口

- `POST /minimax_h3/upload`：接收一个媒体文件并返回元数据（kind、duration、has_audio、宽高）。
- `GET /minimax_h3/capabilities`：返回 av / ffmpeg / ffprobe 解码能力。
- `POST /minimax_h3/probe`：按 `{"file": ...}` 探测时长、音轨、宽高。
- `GET/POST /minimax_h3/presets[/save|load|delete]`：媒体预设的保存/加载/删除。

---

## 节点 7：MiniMax H3 Resolution Selector
<img width="379" height="181" alt="image" src="https://github.com/user-attachments/assets/0978a05f-f040-47d8-a860-ac2df5ff3541" />

与官方 Resolution Selector 类似，但用官方“宽×高”预设替代百万像素滑杆：

- `aspect_ratio`：官方 8 种宽高比（1:1 / 2:3 / 3:2 / 3:4 / 4:3 / 9:16 / 16:9 / 21:9）。
- `size`：只显示当前比例对应的“宽×高”预设，数值沿用官方参考表风格（16:9 使用
  官方尺寸表 608×352 … 1920×1088，其他比例按同一像素面积换算），宽高均为 32 倍数；
  比例与官方参考一致，属于“近似比例”（如 1344×768 对应 16:9、768×1376 对应 9:16）。
- 包含接近常见分辨率的数值：16:9 的 864×480（480p）、1280×736（接近 720p）、
  1344×768（官方原生 768p）；9:16 的 480×864（480p 竖屏）、736×1280（720p 竖屏类）、
  768×1376 等。
- `16:9` 位于 `9:16` 下方；切换比例时下拉选项自动跟随（原生 DynamicCombo，
  无需前端脚本）。

输出：`width`、`height`（INT），以及 `size`（字符串，如 `1344×768`）。

---

## 节点 8：MiniMax H3 Concat AV Latent
<img width="464" height="135" alt="image" src="https://github.com/user-attachments/assets/78c5c939-0349-45dc-956a-deba744752bb" />

参考自 ComfyUI-PT_H3ConcatAVLatent 的 `PT_H3ConcatAVLatent`，转换为插件的新 API
注册（节点 id `MiniMaxH3ConcatAVLatent`，与原插件可共存）。该节点主要用于
**视频的二次采样放大**：把已生成的视频/音频重新编码成 latent，合并后以更高分辨率
或更低步数再次采样（放大 / 重绘）。

- `video_latent`：视频 latent，形状 `[B, 24, T, H/16, W/16]`
- `audio_latent`：音频 latent，形状 `[B, 32, 2, T_audio]`
- 输出 `av_latent`：合并后的联合 `NestedTensor`，直接接 H3 采样器的 latent 输入，
  实现二次采样放大 / 重绘。

---

## 节点 9：MiniMax H3 Face Ref Video

按 ai-toolkit `minimax_h3_ref2va` 的参考视频口径做预处理，输出可直接接到
`MiniMaxH3ReferenceToVideo` 的 `ref_video_i` / `ref_video_audio_i`：

- `video`：任意源帧率的参考视频
- `target_megapixels`：目标生成像素面积，`0.258` 约等于 672×384
- `max_length`：24fps 帧数上限，`0` 表示整段

输出：

- `frames`：按真实时间轴重采样到 24fps，帧数向下吸附到 `17n+5`；统一输出 RGB
- `audio`：裁到与保留帧相同的时间窗，并统一为 32kHz 立体声；无音轨时输出静音占位
- `width` / `height`：按参考视频自身比例、目标像素面积和 /32 网格计算
- `length`：保留下来的 24fps 帧数

本节点是根据该公开行为规格独立实现的 clean-room 版本，没有复制
`ComfyUI-AIToolkit-MiniMaxH3` 的源码。原包未提供许可证文件，因此这里只复用
其公开描述的处理契约。感谢 `ComfyUI-AIToolkit-MiniMaxH3` 原作者公开这套
参考视频预处理口径，也感谢 [ostris/ai-toolkit](https://github.com/ostris/ai-toolkit)
提供了 `minimax_h3_ref2va` 的采样流程参考。

---

## 节点 10：MiniMax H3 Tiled Sampler

在保持单节点结构的前提下，移植了 AVPack 主 `H3TiledSampler` 的分块控制能力
（不包含 FirstPass / ModelPatch 两个额外节点）：

| 参数 | 说明 |
| --- | --- |
| `fusion` | `multidiffusion`：全局 latent 每步融合所有 tile，需要 `sampler=euler`；`independent`：每个 tile 独立跑完整去噪（旧路径） |
| `blend` | 融合窗口：`cosine` 或 `gaussian`（边缘权重更低） |
| `ref_handling` | `auto`/`off`：完整参考透传给每个 tile；`crop`：按 tile 区域裁切参考；`bypass`：检测到 R2V 参考时整图单次采样 |

---

## Credits / License · 版权信息 / 许可

This project is distributed as a whole under GNU GPL v3.0. See
[NOTICE](https://github.com/oufeixinxinren/ComfyUI-MiniMax-ContextIR/blob/main/NOTICE),
[LICENSE](https://github.com/oufeixinxinren/ComfyUI-MiniMax-ContextIR/blob/main/LICENSE),
and
[LICENSES](https://github.com/oufeixinxinren/ComfyUI-MiniMax-ContextIR/blob/main/LICENSES)
for third-party attribution and derivative-work details.

本项目整体以 GNU GPL v3.0 协议发布。有关第三方署名和衍生作品的详细信息，请参阅
[NOTICE](https://github.com/oufeixinxinren/ComfyUI-MiniMax-ContextIR/blob/main/NOTICE) 、
[LICENSE](https://github.com/oufeixinxinren/ComfyUI-MiniMax-ContextIR/blob/main/LICENSE)
和
[LICENSES](https://github.com/oufeixinxinren/ComfyUI-MiniMax-ContextIR/blob/main/LICENSES) 。

This project contains or modifies code / algorithms from:
本项目包含或修改了以下代码 / 算法：

[ComfyUI](https://github.com/comfyanonymous/ComfyUI) — GPL-3.0
[MiniMax-AI / MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3) — 上游仓库未标注许可证
（H3 模型权重见 MiniMax H3 Community License）；本项目包含其官方 Skills
[Adudeguyman / ComfyUI-Fantastic-MiniMaxH3-PromptBuilder](https://github.com/Adudeguyman/ComfyUI-Fantastic-MiniMaxH3-PromptBuilder) — MIT
[ptmaster / ComfyUI-PT_H3ConcatAVLatent](https://github.com/ptmaster/ComfyUI-PT_H3ConcatAVLatent) — 上游未标注许可证 / license not specified
[T8mars / comfyui-minimax-h3-audio-T8](https://github.com/T8mars/comfyui-minimax-h3-audio-T8) — GPL-3.0-or-later
ComfyUI-AIToolkit-MiniMaxH3 — 上游未提供许可证文件；本插件仅按其公开行为说明独立实现，不包含其源码
ComfyUI-MiniMaxH3-AVPack — MIT，Copyright (c) 2026 yc；Tiled Sampler 的 fusion / blend /
ref_handling 语义参考该项目主 Tiled Sampler，并按 MIT 条款署名移植

Special thanks to the original author of ComfyUI-AIToolkit-MiniMaxH3 for publishing
the reference-video preparation behaviour, and to ostris/ai-toolkit for the
`minimax_h3_ref2va` sampling recipe that it documents.
特别感谢 ComfyUI-AIToolkit-MiniMaxH3 原作者公开参考视频预处理行为规格，也感谢
ostris/ai-toolkit 提供 `minimax_h3_ref2va` 采样流程参考。

Thanks to all upstream projects and contributors.
感谢所有上游项目和贡献者。
