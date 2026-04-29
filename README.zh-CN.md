# BananaHub Skill 🍌

[English README](./README.md)

BananaHub 是一个面向 AI 图像工作流的 agent skill：你用中文或混合语言描述需求，它负责整理 prompt、判断运行环境、选择合适的出图路径，并把生成、编辑、模板复用放在同一个 `/bananahub` 入口里。

它不只是“帮你写 prompt”。BananaHub 更像一层图像工作流中台：上接 Agent，对下适配 Gemini / Nano Banana、OpenAI GPT Image、兼容网关和宿主自带图像工具。

## 为什么用 BananaHub

- **不挑环境**：有 API key 就本地直连出图；宿主带图像工具就委托宿主；什么都没有也能产出可复用 prompt。
- **少返工**：先锁定文字、结构、保留项和编辑边界，再生成，减少“画得好但不对”的结果。
- **多模型但不乱用**：prompt 优化、模板发现、归档是跨模型能力；尺寸、mask、参考图、质量档位这些按 provider/model 能力路由。
- **prompt 可追踪**：支持把最终 prompt 自动归档，方便复盘、复用、交付或继续迭代。
- **模板可扩展**：内置高频模板，也能从 BananaHub 搜索、安装、激活更多 prompt / workflow 模板。

## 快速开始

```bash
# Open Agent Skills / skills.sh
npx skills add https://github.com/bananahub-ai/bananahub-skill --skill bananahub

# 或直接安装到 Claude Code
claude skill install https://github.com/bananahub-ai/bananahub-skill

/bananahub init
/bananahub 一只橘猫趴在键盘上打盹
```

想先看当前会走哪条执行路径：

```bash
python3 scripts/bananahub.py check-mode --pretty
```

## 三种运行模式

| 模式 | 什么时候触发 | BananaHub 会怎么做 |
|---|---|---|
| `provider-backed` | 本地配置了可用 provider 和 key | 优化 prompt，调用 provider 出图或编辑，并保存结果 |
| `host-native` | 本地 provider 不完整，但宿主 Agent 有图像工具 | 优化 prompt，必要时归档，然后交给宿主图像工具出图 |
| `prompt-only` | 没有可用 provider，也没有宿主图像工具 | 只产出高质量 prompt；不会假装已经出图 |

CLI 里可以用 `BANANAHUB_HOST_IMAGEGEN=1` 或 `check-mode --host-imagegen` 显式声明宿主有图像工具。

## 适合哪些场景

- **日常高频出图**：产品白底图、背景替换、文章一图流、信息图、代码库讲解图。
- **知识表达**：把流程、长文、代码结构压缩成一张能快速读懂的图。
- **多模型团队**：同一套模板 ID 同时支持 Gemini / Nano Banana 和 OpenAI GPT Image，并保留模型差异。
- **可复用流程**：prompt 自动归档，复杂风格包和样例库通过 BananaHub 远程安装，不塞进 skill 本体。

## 常用命令

| 命令 | 用途 |
|---|---|
| `/bananahub <描述>` | 优化 prompt 并生成图片 |
| `/bananahub edit <描述> --input <图片>` | 按文字要求编辑图片 |
| `/bananahub optimize <描述>` | 只优化 prompt，不出图 |
| `/bananahub generate <English prompt>` | 跳过优化，直接用英文 prompt 生成 |
| `/bananahub models` | 查看可用模型 |
| `/bananahub check-mode` | 查看当前运行模式和能力层级 |
| `/bananahub templates` | 列出内置和已安装模板 |
| `/bananahub use <template-id>` | 使用 prompt 模板或启动 workflow 模板 |
| `/bananahub discover <需求>` | 在 BananaHub 搜索并推荐模板 |
| `/bananahub init` | 检查和初始化环境 |

## 常用参数

| 参数 | 说明 |
|---|---|
| `--direct` | 少问少确认，直接生成，但仍保持克制增强 |
| `--raw` | 只翻译 / 整理，不做额外增强 |
| `--model <id>` | 指定模型，如 `gemini-3-pro-image-preview`、`gpt-image-2` |
| `--provider <id>` | 临时指定 provider，如 `openai`、`google-ai-studio` |
| `--aspect <ratio>` | 宽高比，如 `16:9`、`1:1`、`9:16` |
| `--image-size <preset>` | Gemini 原生尺寸档位：`1K`、`2K`、`4K` |
| `--openai-size <value>` | OpenAI 图像接口原生尺寸参数 |
| `--resize <WxH>` | 出图后再缩放到交付尺寸 |
| `--output <path>` | 指定图片输出路径 |
| `--save-prompt` | 把最终 prompt 归档到 `bananahub-prompts/` |
| `--prompt-output <path>` | 把最终 prompt 保存到指定文件或目录 |
| `--input <path>` | 编辑命令的输入图片 |
| `--ref <path...>` | 编辑时附加参考图 |
| `--mask <path>` | OpenAI-native mask 编辑 |

也可以设置 `BANANAHUB_SAVE_PROMPTS=1`，让 generate/edit 默认归档最终 prompt。

## Prompt 归档

prompt 归档用于复盘和复用，尤其适合团队交付、模板调试和多轮实验。

```bash
python3 scripts/bananahub.py generate \
  "A clean product photo of a blue wireless earbud case" \
  --save-prompt

python3 scripts/bananahub.py generate \
  "A launch poster for BananaHub" \
  --prompt-output docs/prompts/launch-poster.md
```

归档文件会包含命令、provider、模型、时间和最终 prompt。即使 provider 调用失败，prompt 也会先保存，方便换模型或交给宿主图像工具继续执行。

## Provider 接入

BananaHub 支持多条接入路径。高级能力不要跨 provider 猜测，实际以 `check-mode` 和 capability registry 为准。

| Provider | 适合谁 | 生成 | 编辑 | Mask | 备注 |
|---|---|---:|---:|---:|---|
| `google-ai-studio` | 默认推荐，个人和团队快速接入 | ✅ | ✅ | — | Gemini / Nano Banana 路线 |
| `gemini-compatible` | Gemini 风格中转 / 代理 | ✅ | ✅ | — | 取决于中转实现 |
| `vertex-ai` | 企业 GCP / Vertex AI | ✅ | ✅ | — | 支持 ADC 或 API key |
| `openai` | OpenAI GPT Image 官方接口 | ✅ | ✅ | ✅ | GPT Image native 路线 |
| `openai-compatible` | OpenAI 风格网关 | ✅ | 视网关而定 | 视网关而定 | 不默认假设高级能力 |
| `chatgpt-compatible` | Chat/completions 返回图片的接口 | ✅ | — | — | 尽力解析图片 URL 或 base64 |

配置示例：

```bash
# 查看当前配置来源和能力
python3 scripts/bananahub.py config show
python3 scripts/bananahub.py check-mode --pretty

# Google AI Studio / Gemini Developer API
python3 scripts/bananahub.py config set --provider google-ai-studio --api-key <your_api_key>

# Gemini-compatible 中转
python3 scripts/bananahub.py config set --provider gemini-compatible --base-url https://your-gemini-endpoint --api-key <your_key>

# OpenAI GPT Image
python3 scripts/bananahub.py config set --provider openai --api-key <your_openai_key> --model gpt-image-2

# OpenAI-compatible 网关
python3 scripts/bananahub.py config set --provider openai-compatible --base-url https://your-openai-compatible-endpoint --api-key <your_key>

# Chat/completions-compatible 图像接口
python3 scripts/bananahub.py config set --provider chatgpt-compatible --base-url https://your-chat-endpoint --api-key <your_key> --model gpt-5.4

# Vertex AI
python3 scripts/bananahub.py config set --provider vertex-ai --auth-mode adc --project <gcp-project> --location global
```

配置来源优先级：`--config <file>` → 环境变量 → `~/.config/bananahub/config.json`。

## Prompt 优化怎么工作

```text
用户输入
  │
  ├─ 提取约束：精确文字 / 保留项 / 避免项 / 平台 / 编辑不变量
  ├─ 基础整理：修正关键词堆砌、SD/MJ 语法、负面描述、主体埋太深等问题
  ├─ 智能翻译：描述性内容默认转英文；图中文字、专名和标签保留原文
  ├─ 识别意图：photo / product / diagram / sticker / text-heavy / 3d / concept-art ...
  └─ 克制增强：只补对结果有帮助的细节；高影响方向默认先确认
```

这套能力是跨模型的。真正依赖 provider 的能力，比如 mask edit、精确尺寸、透明背景、质量档位、参考图数量，会交给 provider/model 层判断。

## 模板生态

模板分两类：

- **prompt 模板**：适合一次组装一个稳定 prompt，例如产品白底图、信息图卡片、背景替换编辑。
- **workflow 模板**：适合多步任务，例如文章一图流解读、代码库讲解图。

```bash
/bananahub templates
/bananahub templates article-one-page-summary
/bananahub use info-diagram "PR 评审流程：Change、Review、Test、Fix、Merge"
/bananahub use background-replace-edit --input product.png
/bananahub discover logo system
/bananahub create-template
```

内置模板是轻量 starter pack：`product-white-bg`、`info-diagram`、`article-one-page-summary`、`repo-explainer-diagram`、`background-replace-edit`。它们偏高频、低维护、不带重样图，并通过 provider-specific prompt variants 同时支持 Gemini / Nano Banana 和 OpenAI GPT Image。

更丰富的官方模板已经迁到 `bananahub-ai/templates`，可通过 BananaHub discovery 远程安装，比如风格包、Logo 系统、角色一致性、Campaign 视觉、带样图的模板库。社区模板仍通过更大的 catalog 发现。用户安装的模板保存在 `~/.config/bananahub/templates/`，同名时优先使用用户模板。

## 参考文档

- Prompt 规则：`references/prompt-guide.md`
- 能力分层：`references/capability-registry.md`
- 模型注册：`references/model-registry.json`
- 模板规范：`references/template-format-spec.md`
- 官方参考来源：`references/official-sources.md`

## 运行要求

- 支持 Skill 的 Claude Code / Open Agent Skills 运行环境
- Python 3.8+
- 可选：`google-genai`、`pillow`
- 可选：Gemini、OpenAI 或兼容网关 API key

## License

- 代码、脚本和通用文档：MIT
- `references/templates/` 下的内置 starter 模板：默认 CC BY 4.0，除非模板目录另有说明
