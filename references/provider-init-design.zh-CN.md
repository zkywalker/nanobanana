# BananaHub 接入与初始化降本方案

**状态**：historical proposal; current runtime default is `openai-compatible` + `gpt-image-2`
**日期**：2026-04-09
**范围**：`bananahub-skill`

## 1. 背景

当前 BananaHub 的初始化能力，核心还是围绕一套很窄的配置模型：

- 一个 `api_key`
- 一个可选 `base_url`
- 一个默认走 `google-genai` SDK 的客户端创建方式

这对最基础的 AI Studio key 能跑，但对以下场景都不够友好：

- 用户只有 Google AI Studio / Gemini Developer API key，希望 1 分钟内接好
- 用户使用三方中转站，希望直接填 `base_url + key`
- 用户走 Vertex AI / 企业 GCP 账号，希望用 `project + location + ADC`
- 用户已经在自己的系统里统一走 OpenAI-compatible 网关，希望复用同一套网关配置
- 后续想支持“某些场景用某个模型提供商”的路由，但现有 runtime 没有 provider 抽象

## 2. 现状结论

从当前实现看：

- 配置项只有 `api_key` / `base_url`，没有 `provider`、`auth_mode`、`project`、`location` 等语义
- 环境变量只认 `GEMINI_API_KEY`，没有兼容 Google 官方文档常见的 `GOOGLE_API_KEY`
- `init` 的交互还是“你给我 key 和 base_url”，不是“你想走哪条接入路线”
- runtime 只有一套 `genai.Client(api_key=..., http_options=...)` 逻辑

对应代码位置：

- 配置键与环境变量别名定义：`scripts/bananahub.py`
- 客户端创建：`scripts/bananahub.py`
- 初始化流程：`scripts/bananahub.py`
- Skill 层引导：`references/init-guide.md`

## 3. 当前可行接入途径

### A. Google AI Studio / Gemini Developer API

这是适合 Gemini / Nano Banana 用户的官方路径。当前 BananaHub 的默认开箱路径已经改为 `openai-compatible` + `gpt-image-2`。

特点：

- 用户只需要一个 API key
- 适合个人用户、轻量使用、最快起步
- BananaHub 应保留它作为一键可选路径，但不再把它作为默认推荐路径

建议输入方式：

- `api_key`
- 可选 `model`

建议 runtime：

- `google-genai` SDK
- 或 Gemini Developer API REST

### B. Vertex AI

这是企业和团队场景更稳的官方路径。

特点：

- 身份模式不再只是 API key，还可能是 ADC / service account / GCP 项目权限
- 需要 `project`、`location`
- 适合后续扩展到更完整的云侧治理、限额、审计和企业环境

建议输入方式：

- `project`
- `location`
- `auth_mode=adc|api_key`
- 可选 `api_key`

建议 runtime：

- `google-genai` SDK 的 Vertex 模式

### C. OpenAI-compatible Gemini Endpoint

Google 官方已经提供 Gemini 的 OpenAI-compatible 入口。这个入口的价值不在“比原生更好”，而在“可以并入用户已有的 OpenAI 生态”。

特点：

- 适合已经有 OpenAI 风格网关、SDK、配置面板的用户
- 对接方式天然符合“`base_url + key`”
- 非常适合 BananaHub 做统一 provider 抽象

建议输入方式：

- `base_url`
- `api_key`
- `transport=openai`

建议 runtime：

- 优先直接走 HTTP，避免为了一个兼容层再引入一套重 SDK

### D. 三方 Gemini-compatible / OpenAI-compatible 中转

这类路线是降低接入门槛的重要补充，但要明确它是“兼容模式”，不是 BananaHub 能保证稳定支持的官方标准面。

特点：

- 用户最常见输入就是 `base_url + key`
- 不同站点的路径、鉴权头、模型名、错误格式都可能不同
- 不能把它和 Google 官方路径混成一套黑盒逻辑

建议输入方式：

- `provider=gemini-compatible` 或 `provider=openai-compatible`
- `base_url`
- `api_key`
- 可选 `model_map`

建议 runtime：

- 不要继续把它硬塞给当前那套 `genai.Client(api_key=..., http_options["base_url"])`
- 应该拆成显式 adapter

## 4. 核心判断

要把 skill 往“开箱即用”推进，关键不是继续往 `config.json` 里多塞几个字段，而是把“接入途径”抽象成 provider。

也就是说，初始化的最小单位不该是：

- 请填 key
- 请填 base_url

而应该是：

- 你想接哪一类入口？
- 这一类入口最少需要什么？
- 我用哪种 runtime 去验证它？

## 5. 建议的配置模型 v2

```json
{
  "provider": "google-ai-studio",
  "transport": "genai",
  "auth_mode": "api_key",
  "api_key": "",
  "base_url": "",
  "project": "",
  "location": "global",
  "model": "",
  "capabilities": {
    "image_generate": true,
    "image_edit": true,
    "list_models": true
  }
}
```

补充字段建议：

- `provider`: `google-ai-studio | vertex-ai | gemini-compatible | openai-compatible`
- `transport`: `genai | gemini-rest | openai-rest`
- `auth_mode`: `api_key | adc`
- `model`: 用户偏好的默认模型
- `model_map`: 三方站点模型名映射
- `healthcheck`: 最近一次探活结果

## 6. 建议的 adapter 设计

在 runtime 层新增 provider adapter，而不是把所有逻辑堆在 `get_client()`。

统一接口建议：

```text
resolve_config()
validate_config()
healthcheck()
list_models()
generate_image()
edit_image()
normalize_error()
```

首批只做 4 个 adapter：

1. `GoogleAiStudioAdapter`
2. `VertexAiAdapter`
3. `GeminiCompatibleAdapter`
4. `OpenAICompatibleAdapter`

其中：

- `GoogleAiStudioAdapter` 继续用 `google-genai`
- `VertexAiAdapter` 走官方 Vertex 模式
- `GeminiCompatibleAdapter` 走 Gemini 风格 REST
- `OpenAICompatibleAdapter` 走 OpenAI 风格 REST

## 7. 初始化流程重设计

### Step 1. 先识别入口类型，不先问裸 key

新版 `/bananahub init` 第一问应该是：

1. 你要接哪种入口？
2. 官方 AI Studio
3. Vertex AI
4. 三方 Gemini-compatible
5. 三方 OpenAI-compatible

### Step 2. 每类入口只问最少字段

#### AI Studio

- 只问 `api_key`
- 可选问默认模型
- 默认不问 `base_url`

#### Vertex AI

- 问 `project`
- 问 `location`
- 问 `auth_mode`
- 如果 `auth_mode=api_key` 再问 key

#### 三方站点

- 先问它更像 `Gemini-compatible` 还是 `OpenAI-compatible`
- 再问 `base_url`
- 再问 `api_key`
- 可选问默认模型

### Step 3. 做 provider-aware 探活

探活不能再是单一的 `client.models.generate_content("Say OK")`。

建议：

- 文本探活：检查鉴权和最基本可用性
- 模型探活：若 provider 支持列模型，优先拉模型
- 图像探活：只在用户明确需要时做，避免初始化就消耗成本

### Step 4. 保存为标准化配置

无论用户怎么输入，最终都落成 v2 结构。

同时保留对旧配置的兼容读取：

- 只有 `api_key` 时，默认映射成 `google-ai-studio`
- 有 `api_key + base_url` 时，默认映射成 `gemini-compatible`

## 8. 降低初始化成本的具体手段

### 8.1 官方路径做成零思考默认项

默认文案不要再是“请提供 Gemini key 和可选 base_url”，而是：

- 推荐：`Google AI Studio key`
- 备选：`我用的是三方站点`
- 企业：`我用 Vertex AI`

这样大多数用户不用先理解架构。

### 8.2 支持一行式快速配置

新增快捷命令：

```bash
python3 scripts/bananahub.py config quickset --provider google-ai-studio --api-key <KEY>
python3 scripts/bananahub.py config quickset --provider gemini-compatible --base-url <URL> --api-key <KEY>
python3 scripts/bananahub.py config quickset --provider openai-compatible --base-url <URL> --api-key <KEY>
python3 scripts/bananahub.py config quickset --provider vertex-ai --project <PROJECT> --location global
```

让 `init` 和手动配置走同一个标准写入层。

### 8.3 增加环境变量兼容层

至少补上：

- `GOOGLE_API_KEY`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_GENAI_USE_VERTEXAI`

同时继续兼容现有：

- `GEMINI_API_KEY`
- `GOOGLE_GEMINI_BASE_URL`
- `GEMINI_BASE_URL`
- `BANANAHUB_BASE_URL`

### 8.4 为常见 provider 准备 preset

不要硬编码具体商业站点，但可以有 preset 机制：

```json
{
  "id": "generic-openai-compatible",
  "provider": "openai-compatible",
  "required": ["base_url", "api_key"],
  "optional": ["model"]
}
```

后续如果要支持某些常见供应商，只要新增 preset，不改 runtime 主流程。

## 9. 推荐的实施顺序

### Phase 1: 先把“主路径更顺”

目标：1 个版本内就能显著降低初始化成本。

内容：

- 新增 `provider` 配置模型
- 支持 `GOOGLE_API_KEY`
- 重写 `init` 问答与探活逻辑
- 保持旧配置兼容
- `config show` 展示 provider 和 transport

### Phase 2: 官方多入口

内容：

- 增加 `VertexAiAdapter`
- 增加 `OpenAICompatibleAdapter`
- 把 healthcheck 按 provider 拆开

### Phase 3: 三方兼容生态

内容：

- 新增 provider preset 注册表
- 模型名映射
- 更稳的错误归一化
- 按 provider 标记支持能力

## 10. 不建议的做法

### 不建议继续把所有三方站点都塞进当前 `base_url` 黑盒

原因：

- 不同站点不一定真兼容 Google SDK 的调用细节
- 错误不可解释
- 后续支持 OpenAI-compatible 或 Vertex 时会越来越乱

### 不建议一开始就做“全模型提供商大统一”

原因：

- BananaHub 当前定位仍是 Gemini / Nano Banana 图像工作流
- 真正值得先做的是“多入口同体验”，不是“所有模型全支持”

## 11. 结论

建议把 BananaHub 的接入策略定成三层：

1. **默认主路径**：`Google AI Studio key`
2. **兼容逃生口**：`base_url + key`
3. **企业路径**：`Vertex AI`

实现上以 `provider adapter` 为中心重构初始化与 runtime，而不是继续扩展单一的 `api_key/base_url` 模型。

这样做的收益是：

- 默认用户最快可用
- 三方中转站能低成本接入
- 企业场景有正规入口
- 后续如果要加“某些场景下的模型提供商支持”，不需要再推翻初始化层

## 12. 参考来源

- Google Gemini API image generation: https://ai.google.dev/gemini-api/docs/image-generation
- Google Gen AI SDK for Python: https://googleapis.github.io/python-genai/
- Gemini API OpenAI compatibility: https://ai.google.dev/gemini-api/docs/openai
- Gemini partner / gateway integrations: https://ai.google.dev/gemini-api/docs/partner-integration
- Vertex AI image generation: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/image-generation
- Vertex AI API keys: https://cloud.google.com/vertex-ai/generative-ai/docs/start/api-keys
- Google Cloud ADC: https://cloud.google.com/docs/authentication/application-default-credentials
