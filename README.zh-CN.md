# BananaHub Skill 🍌

[English README](./README.md)

BananaHub 是一个用于 Gemini 生图与编辑的 Skill。它会把非英语图像需求默认整理成更稳的英文 prompt，再通过同一个 `/bananahub` 入口完成生成、编辑和模板化复用。

## 快速开始

```bash
# Open Agent Skills / skills.sh 安装方式
npx skills add https://github.com/bananahub-ai/bananahub-skill --skill bananahub

# 或直接安装到 Claude Code
claude skill install https://github.com/bananahub-ai/bananahub-skill

/bananahub init
/bananahub 一只橘猫趴在键盘上打盹
```

## 产品定位

BananaHub 的目标是用一个 skill 覆盖完整的 Gemini 生图工作流，而不是拆成很多小入口：

- **一个命令面**：优化、出图、编辑、套模板、继续迭代，都在同一段对话里通过 `/bananahub` 完成
- **渐进式披露引导**：低风险整理默认静默完成，只有在歧义会明显影响结果时才追问，命中高匹配模板时才提示切换
- **可安装的模板生态**：常见任务由内置模板覆盖，额外能力通过 BananaHub 按需安装；模板既可以是单步 prompt，也可以是多步 workflow，但基础 skill 仍保持单一入口

BananaHub 的优化链路和模板方法，基于 Google / Gemini 官方图像生成文档、Prompt Guide 与公开最佳实践提炼，并结合真实工作流做了约束优先和 agent-native 的封装。参考来源见 [references/official-sources.md](references/official-sources.md)。

## 主要能力

1. **把非英语描述整理成更稳的英文 prompt**：顺手修正常见问题，比如关键词堆砌、SD/MJ 式写法、负面描述过多等
2. **按图像类型做克制的增强**：会判断需求更像照片、插画、图示、重文字版式、极简风、贴纸、3D、产品图还是概念设计，只补有必要的细节
3. **保留需要出现在画面里的原文**：比如 `写着"生日快乐"的蛋糕`，图里的 `"生日快乐"` 不会被翻掉
4. **先抽约束，再出图**：先识别精确文字、必须保留和必须避开的内容、用途和编辑不变量，再开始生成
5. **三种工作模式**：默认模式会和你确认关键增强项；`--direct` 直接生成；`--raw` 只翻译、不优化
6. **模板化复用和分发**：支持内置模板、AI 引导式模板创建，以及通过 BananaHub 搜索和安装扩展模板

## 处理原则

- 有几种可能方向，而且结果会差很多时，先问，不乱猜
- 不随便加重口味细节：背景、配色、光线氛围、镜头语言、材质、额外道具这些都尽量克制
- 做海报、Logo、图表、信息图时，把文字和结构当成锁定内容
- 最终 prompt 默认统一成英文，保证表达更稳定；只有图中文字、专有名称或必须保留的标签继续保留原文
- 做编辑时先保住不该变的部分，只改用户点名要改的那一项
- 迭代时一次只动一个主要变量，方便收敛

## 安装

```bash
npx skills add https://github.com/bananahub-ai/bananahub-skill --skill bananahub

# 或直接安装到 Claude Code
claude skill install https://github.com/bananahub-ai/bananahub-skill
```

主命令：`/bananahub`

兼容说明：
- 旧的 `~/.config/nanobanana/` 配置目录仍然会作为 fallback 继续读取。
- `scripts/nanobanana.py` 仍然保留为 legacy 入口，但主入口已经切到 `scripts/bananahub.py`。

## 初始化

装好后先跑一次初始化，把环境配齐：

```bash
/bananahub init
```

这个命令会做三件事：

- 检查 Python 依赖：`google-genai`、`pillow`
- 引导你把 Gemini API Key 配到支持的配置来源里
- 在基础环境就绪后测试 API 是否可用

如果你想先手动装依赖，可以直接运行：

```bash
python3 -m pip install --user google-genai pillow
```

**Gemini API Key 申请地址**：https://aistudio.google.com/apikey（有免费额度）

## 基本用法

```bash
/bananahub 一只橘猫趴在键盘上打盹
```

### 命令

| 命令 | 说明 |
|---|---|
| `/bananahub <描述>` | 优化 prompt 并生成图片 |
| `/bananahub edit <描述> --input <图片>` | 按文字要求编辑现有图片 |
| `/bananahub optimize <描述>` | 只优化 prompt，不生成 |
| `/bananahub generate <English prompt>` | 直接用英文 prompt 生成 |
| `/bananahub models` | 列出可用模型 |
| `/bananahub discover <需求>` | 搜索 BananaHub 并推荐可安装模板 |
| `/bananahub discover trending` | 查看当前热门 BananaHub 模板 |
| `/bananahub init` | 检查并初始化环境 |
| `/bananahub help` | 查看帮助 |

### 参数

| 参数 | 说明 |
|---|---|
| `--direct` | Skill 层直出模式：跳过确认，但仍保持克制增强 |
| `--raw` | Skill 层 Raw 模式：只翻译，不做优化 |
| `--model <id>` | 指定模型（`gemini-3-pro-image-preview`、`gemini-3.1-flash-image-preview` 或 `gemini-2.5-flash-image`） |
| `--aspect <ratio>` | 宽高比，比如 `16:9`、`1:1`、`9:16` |
| `--image-size <preset>` | 原生出图尺寸档位（`1K`、`2K`、`4K`） |
| `--resize <WxH>` | 生成/编辑后的后处理缩放 |
| `--size <value>` | 兼容旧参数：`1K/2K/4K` 表示原生出图尺寸，`WxH` 表示后处理缩放 |
| `--output <path>` | 指定输出文件路径 |
| `--input <path>` | 编辑命令的输入图片 |

### 示例

```bash
# 常规用法：先优化，再确认
/bananahub 赛博朋克风格的东京街头夜景

# 直出模式：不再逐项确认
/bananahub 水彩风格的猫咪 --direct

# Raw 模式：只翻译，不做额外整理
/bananahub 一个简单的红色圆圈 --raw

# 指定宽高比、模型和原生出图尺寸
/bananahub 山水画风格的桂林风景 --aspect 16:9 --model gemini-2.5-flash-image --image-size 2K

# 贴纸 / 表情包
/bananahub 画一个开心的柴犬表情包

# 3D 渲染
/bananahub 等距视角的咖啡店室内设计

# 产品图
/bananahub 白底蓝牙耳机产品图

# 概念设计
/bananahub 赛博朋克风格的女性角色设计

# 编辑现有图片
/bananahub edit 把背景换成海滩 --input photo.png

# 先原生 2K 出图，再缩放到交付尺寸
/bananahub edit 添加一顶圣诞帽 --input avatar.png --image-size 2K --resize 1024x1024 --output avatar_xmas.png
```

## 模板

内置模板是一组可复用的 agent 模块。有些模板是 `prompt` 类型，用来组装单步 prompt；有些模板是 `workflow` 类型，用来加载渐进式披露的多步 SOP。你可以直接用默认值，也可以只覆盖关心的部分；如果某类任务值得反复复用，就去 BananaHub 安装对应模块，而不是把基础 skill 塞得越来越重。

### 模板相关命令

| 命令 | 说明 |
|---|---|
| `/bananahub templates` | 列出全部模板 |
| `/bananahub templates <name>` | 按模板类型查看详情 |
| `/bananahub use <name>` | 激活 prompt 模板或启动 workflow 模板 |
| `/bananahub use <name> <描述>` | 带自定义变量或上下文激活模板 |
| `/bananahub discover <需求>` | 搜索 BananaHub 并推荐远程模板 |
| `/bananahub create-template` | 打开 AI 引导式 prompt/workflow 模板创建向导 |

### 模板示例

```bash
# 列出全部模板
/bananahub templates

# 查看模板详情
/bananahub templates cyberpunk-city

# 直接用 prompt 模板默认值生成
/bananahub use cyberpunk-city

# 用补充描述覆盖 prompt 模板变量
/bananahub use cyberpunk-city 东京新宿街头，紫色和金色霓虹

# 启动 workflow 模板
/bananahub use consistent-character-storyboard

# 给文章或教程规划分节配图
/bananahub use article-illustration-workflow docs/guide.md

# 让 skill 去 BananaHub 找合适模板
/bananahub discover logo 品牌标识

# 配合参数使用
/bananahub use cyberpunk-city 上海外滩未来版 --aspect 9:16
```

### Workflow 样章

`consistent-character-storyboard` 是内置的多步 workflow 模板示例，它的目标不是一键出最终图，而是做“角色一致性分镜探索”。

常见用法：

```bash
# 第一步：先做或确认一张母图
/bananahub 一个可爱的暹罗猫IP，奶油色毛发，深棕色重点色，蓝眼睛，戴青绿色小围巾和金色铃铛

# 第二步：启动 workflow 模板
/bananahub use consistent-character-storyboard
```

### 内置模板

| ID | 模板类型 | 标题 | Profile |
|---|---|---|---|
| `cyberpunk-city` | prompt | 赛博朋克城市夜景 | photo |
| `cute-sticker` | prompt | Q版贴纸表情包 | sticker |
| `product-white-bg` | prompt | 电商白底产品图 | product |
| `info-diagram` | prompt | 信息图 / 流程图 | diagram |
| `minimal-wallpaper` | prompt | 极简手机壁纸 | minimal |
| `consistent-character-storyboard` | workflow | 角色一致性分镜工作流 | general |
| `repo-explainer-diagram` | workflow | 代码库讲解图工作流 | diagram |
| `readme-launch-visual` | workflow | README 启动视觉工作流 | text-heavy |
| `article-illustration-workflow` | workflow | 文章配图工作流 | diagram |
| `asset-style-consistency-pack` | workflow | 本地素材风格统一工作流 | general |

### 安装更多模板（BananaHub）

如果你想让 skill 自动去 BananaHub 搜索、排序并衔接安装与激活，优先直接用 `/bananahub discover <需求>`。

```bash
# 让 skill 代你搜索 BananaHub
/bananahub discover 代码库讲解图

# 直接用 CLI 搜索 BananaHub
npx bananahub search <关键词>

# 已知安装目标时，直接从 GitHub 安装
npx bananahub add <username>/<repo>
```

用户安装的模板保存在 `~/.config/bananahub/templates/`。如果和内置模板 ID 冲突，用户模板优先。

### 自己创建模板

运行 `/bananahub create-template` 会进入一个引导式向导：先判断是 `prompt` 还是 `workflow` 模板，再整理内容草稿，必要时生成样例，最后组装成模板文件。最终产物是一个可直接发到 GitHub，或者提交到 BananaHub 的 `template.md`。

`prompt` 模板使用 `{{变量名|默认值}}` 占位符、变量表和 tips 区块；`workflow` 模板使用 `Goal`、`Inputs`、`Steps`、`Prompt Blocks` 这类多步结构。完整规范见 `references/template-format-spec.md`。

发布前检查：

- 每张样图文件名都带上生成模型缩写，比如 `sample-3-pro-01.png`
- `template.md` 里的样图元数据要写全：`file`、`model`、`prompt`、`aspect`
- `README.md` 必须明确写出 `Verified Models`、`Supported Models`、`Sample Outputs`
- `Sample Outputs` 里把每张样图和对应模型、对应 prompt 或变体说明一一对应起来

## Prompt 优化是怎么做的

```text
用户输入（非英语或混合语言）
  │
  ├─ Phase 0: 约束提取
  │   └─ 精确文字 / 保留项 / 避免项 / 平台 / 不变量
  │
  ├─ Phase 1: 基础优化（静默执行）
  │   ├─ 格式纠正（修复关键词堆砌、SD 语法等）
  │   ├─ 智能翻译（描述性内容转英文，图中文字保留原文）
  │   └─ 结构整理 + 保守护栏
  │
  ├─ Phase 2: 意图识别
  │   └─ 匹配 profile：photo / illustration / diagram / text-heavy / minimal / sticker / 3d / product / concept-art / general
  │
  └─ Phase 3: 增强（命中 profile 时）
      └─ 读取对应规则，只补有依据的维度；高影响增强会先征求确认
```

## 可用模型

| 模型 | 别名 | 适合场景 |
|---|---|---|
| `gemini-3-pro-image-preview` | Gemini 3 Pro Image（默认） | 质量优先、复杂场景、文字渲染 |
| `gemini-3.1-flash-image-preview` | Gemini 3.1 Flash Image | 质量和速度更均衡，多轮迭代和文字渲染能力更强 |
| `gemini-2.5-flash-image` | Gemini 2.5 Flash Image | 速度优先、快速试稿 |

`gemini-2.0-flash-preview-image-generation` 仍保留为兼容旧环境的 legacy fallback，但不再是主要推荐的 Flash 模型。

## 项目结构

```text
bananahub-skill/
├── SKILL.md                          # Skill 定义（Claude Code 入口）
├── scripts/
│   ├── bananahub.py                  # 主图片生成入口
│   └── nanobanana.py                 # legacy 兼容入口
└── references/
    ├── prompt-guide.md               # Prompt 优化规则
    ├── official-sources.md           # 权威参考和示例库
    └── profiles/                     # 按意图划分的增强规则
        ├── photo.md
        ├── illustration.md
        ├── diagram.md
        ├── text-heavy.md
        ├── minimal.md
        ├── sticker.md
        ├── 3d.md
        ├── product.md
        ├── concept-art.md
        └── general.md
```

## 运行要求

- 支持 Skill 的 [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.8+
- Gemini API Key（[免费申请](https://aistudio.google.com/apikey)）

## License

MIT
