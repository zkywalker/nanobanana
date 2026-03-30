# Nano Banana 🍌

[English README](./README.md)

Nano Banana 是一个 [Claude Code Skill](https://docs.anthropic.com/en/docs/claude-code/skills)。它会把中文图像需求整理成更适合模型理解的英文 prompt，再通过 Gemini API 生成或编辑图片。

## 产品定位

Nano Banana 不只是一个 prompt 优化器，它更像是 Claude Code 里的 Nano Banana 生图工作流：

- **Agent-native 交互**：优化、出图、编辑、套模板、继续迭代，都在同一段对话里完成
- **渐进式披露引导**：低风险整理默认静默完成，只有在歧义会明显影响结果时才追问，命中高匹配模板时才提示切换
- **可安装的模板生态**：常见任务由内置模板覆盖，额外能力通过 BananaHub 按需安装，不把基础 skill 做成一个大杂烩

## 主要能力

1. **把中文描述整理成更稳的英文 prompt**：顺手修正常见问题，比如关键词堆砌、SD/MJ 式写法、负面描述过多等
2. **按图像类型做克制的增强**：会判断需求更像照片、插画、图示、重文字版式、极简风、贴纸、3D、产品图还是概念设计，只补有必要的细节
3. **保留需要出现在画面里的中文**：比如 `写着"生日快乐"的蛋糕`，图里的 `"生日快乐"` 不会被翻掉
4. **先抽约束，再出图**：先识别精确文字、必须保留和必须避开的内容、用途和编辑不变量，再开始生成
5. **三种工作模式**：默认模式会和你确认关键增强项；`--direct` 直接生成；`--raw` 只翻译、不优化
6. **模板化复用和分发**：支持内置模板、AI 引导式模板创建，以及通过 BananaHub 搜索和安装扩展模板

## 处理原则

- 有几种可能方向，而且结果会差很多时，先问，不乱猜
- 不随便加重口味细节：背景、配色、光线氛围、镜头语言、材质、额外道具这些都尽量克制
- 做海报、Logo、图表、信息图时，把文字和结构当成锁定内容
- 最终 prompt 默认用英文；只有图中文字、专有名称或必须保留的标签继续保留原文
- 做编辑时先保住不该变的部分，只改用户点名要改的那一项
- 迭代时一次只动一个主要变量，方便收敛

## 安装

```bash
claude skill install /path/to/nanobanana
# 或直接从 GitHub 安装
claude skill install https://github.com/nano-banana-hub/nanobanana
```

## 初始化

装好后先跑一次初始化，把环境配齐：

```bash
/nanobanana init
```

这个命令会做三件事：

- 安装 Python 依赖：`google-genai`、`pillow`
- 引导你把 Gemini API Key 配到支持的配置来源里
- 测试 API 是否可用

**Gemini API Key 申请地址**：https://aistudio.google.com/apikey（有免费额度）

## 基本用法

```bash
/nanobanana 一只橘猫趴在键盘上打盹
```

### 命令

| 命令 | 说明 |
|---|---|
| `/nanobanana <中文描述>` | 优化 prompt 并生成图片 |
| `/nanobanana edit <描述> --input <图片>` | 按文字要求编辑现有图片 |
| `/nanobanana optimize <描述>` | 只优化 prompt，不生成 |
| `/nanobanana generate <English prompt>` | 直接用英文 prompt 生成 |
| `/nanobanana models` | 列出可用模型 |
| `/nanobanana init` | 检查并初始化环境 |
| `/nanobanana help` | 查看帮助 |

### 参数

| 参数 | 说明 |
|---|---|
| `--direct` | Skill 层直出模式：跳过确认，但仍保持克制增强 |
| `--raw` | Skill 层 Raw 模式：只翻译，不做优化 |
| `--model <id>` | 指定模型（`gemini-3-pro-image-preview` 或 `gemini-2.0-flash-preview-image-generation`） |
| `--aspect <ratio>` | 宽高比，比如 `16:9`、`1:1`、`9:16` |
| `--size <WxH>` | 输出尺寸，比如 `1024x1024` |
| `--output <path>` | 指定输出文件路径 |
| `--input <path>` | 编辑命令的输入图片 |

### 示例

```bash
# 常规用法：先优化，再确认
/nanobanana 赛博朋克风格的东京街头夜景

# 直出模式：不再逐项确认
/nanobanana 水彩风格的猫咪 --direct

# Raw 模式：只翻译，不做额外整理
/nanobanana 一个简单的红色圆圈 --raw

# 指定宽高比和模型
/nanobanana 山水画风格的桂林风景 --aspect 16:9 --model gemini-2.0-flash-preview-image-generation

# 贴纸 / 表情包
/nanobanana 画一个开心的柴犬表情包

# 3D 渲染
/nanobanana 等距视角的咖啡店室内设计

# 产品图
/nanobanana 白底蓝牙耳机产品图

# 概念设计
/nanobanana 赛博朋克风格的女性角色设计

# 编辑现有图片
/nanobanana edit 把背景换成海滩 --input photo.png

# 编辑并指定输出文件
/nanobanana edit 添加一顶圣诞帽 --input avatar.png --output avatar_xmas.png
```

## 模板

内置模板是一组已经整理好的 prompt 模块，带可替换变量。你可以直接用默认值，也可以只覆盖关心的变量；如果某类任务值得反复复用，就去 BananaHub 安装对应模块，而不是把基础 skill 塞得越来越重。

### 模板相关命令

| 命令 | 说明 |
|---|---|
| `/nanobanana templates` | 列出全部模板 |
| `/nanobanana templates <name>` | 查看模板详情、变量和使用建议 |
| `/nanobanana use <name>` | 直接用模板默认值生成 |
| `/nanobanana use <name> <描述>` | 用自定义描述覆盖变量后生成 |
| `/nanobanana create-template` | 打开 AI 引导式模板创建向导 |

### 模板示例

```bash
# 列出全部模板
/nanobanana templates

# 查看模板详情
/nanobanana templates cyberpunk-city

# 直接用默认值生成
/nanobanana use cyberpunk-city

# 用补充描述覆盖模板变量
/nanobanana use cyberpunk-city 东京新宿街头，紫色和金色霓虹

# 配合参数使用
/nanobanana use cyberpunk-city 上海外滩未来版 --aspect 9:16
```

### 内置模板

| ID | 标题 | 类型 |
|---|---|---|
| `cyberpunk-city` | 赛博朋克城市夜景 | photo |
| `cute-sticker` | Q版贴纸表情包 | sticker |
| `product-white-bg` | 电商白底产品图 | product |
| `info-diagram` | 信息图 / 流程图 | diagram |
| `minimal-wallpaper` | 极简手机壁纸 | minimal |

### 安装更多模板（BananaHub）

```bash
# 搜索社区模板
npx bananahub search <关键词>

# 从 GitHub 安装模板
npx bananahub add <username>/<repo>
```

用户安装的模板保存在 `~/.config/nanobanana/templates/`。如果和内置模板 ID 冲突，用户模板优先。

### 自己创建模板

运行 `/nanobanana create-template` 会进入一个 4 阶段向导：先确认意图，再整理 prompt 草稿，接着生成样例，最后组装成模板文件。最终产物是一个可直接发到 GitHub，或者提交到 BananaHub 的 `template.md`。

模板格式使用 `{{变量名|默认值}}` 占位符，并配合变量表和 tips 区块。完整规范见 `references/template-format-spec.md`。

发布前检查：

- 每张样图文件名都带上生成模型缩写，比如 `sample-3-pro-01.png`
- `template.md` 里的样图元数据要写全：`file`、`model`、`prompt`、`aspect`
- `README.md` 必须明确写出 `Verified Models`、`Supported Models`、`Sample Outputs`
- `Sample Outputs` 里把每张样图和对应模型、对应 prompt 或变体说明一一对应起来

## Prompt 优化是怎么做的

```text
用户输入（中文）
  │
  ├─ Phase 0: 约束提取
  │   └─ 精确文字 / 保留项 / 避免项 / 平台 / 不变量
  │
  ├─ Phase 1: 基础优化（静默执行）
  │   ├─ 格式纠正（修复关键词堆砌、SD 语法等）
  │   ├─ 智能翻译（描述转英文，图中文字保留原文）
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
| `gemini-3-pro-image-preview` | Nano Banana Pro（默认） | 质量优先、复杂场景、文字渲染 |
| `gemini-2.0-flash-preview-image-generation` | Nano Banana Flash | 速度优先、快速试稿 |

## 项目结构

```text
nanobanana/
├── SKILL.md                          # Skill 定义（Claude Code 入口）
├── scripts/
│   └── nanobanana.py                 # 图片生成 CLI 工具
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
