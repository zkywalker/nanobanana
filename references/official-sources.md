# 官方参考资料索引

本文件沉淀 Nano Banana / Gemini 图像生成的权威信息来源，供 Profile 迭代和即时调研使用。
最后更新：2026-04-03

---

## 一级来源（Google 官方）

### 1. Gemini API 图像生成文档
- **URL**: https://ai.google.dev/gemini-api/docs/image-generation
- **内容**: API 调用方式、支持的模型、参数说明、基础 prompt 示例
- **关键要点**:
  - "Describe the scene, don't just list keywords" 是核心原则
  - 支持 text-to-image、image+text-to-image、多图合成、迭代编辑
  - 最多可混合 14 张参考图
  - 官方限制说明里写明：**For best performance** 支持多种语言，不只是英文；当前包括 `EN`、`es-MX`、`ja-JP`、`zh-CN`、`hi-IN` 等

### 2. Gemini API Imagen Prompt Guide
- **URL**: https://ai.google.dev/gemini-api/docs/imagen-prompt-guide
- **内容**: Imagen 的生成参数、Prompt 写法和示例
- **关键要点**:
  - 官方明确写明：**Imagen supports English only prompts at this time**
  - 这可以作为“为什么很多 Google 图像生成资料都偏向英文 prompt”的直接依据，但它针对的是 Imagen，不是 Nano Banana 原生能力

### 3. Vertex AI Imagen 编辑 API 语言说明
- **URL**: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-api-edit
- **内容**: Imagen 编辑 API 参数定义，含 `language` 字段行为
- **关键要点**:
  - `language: auto` 时，如果检测到受支持语言，Imagen 会把 prompt 自动翻译成英文
  - 如果语言不受支持，则直接按原文处理，官方注明这可能导致 `unexpected output`

### 4. Google DeepMind Prompt Guide
- **URL**: https://deepmind.google/models/gemini-image/prompt-guide/
- **内容**: 五要素框架（Style, Subject, Setting, Action, Composition）、分类技巧、编辑迭代方法
- **关键要点**:
  - 文字渲染：用引号包裹文本，描述字体风格
  - 本地化：提供精确翻译文本 + 文化线索
  - 角色一致性：上传参考图 + 命名角色
  - 五维编辑：角色、构图、动作、场景、风格可独立调整

### 5. Google Developers Blog — 提示词最佳实践
- **URL**: https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/
- **内容**: 按图片类型分类的详细 prompt 策略和示例
- **关键要点**:
  - 写实摄影模板："A photorealistic [shot type] of [subject], [action], set in [environment]. Illuminated by [lighting], creating [mood]. Captured with [camera/lens]."
  - 插画/贴纸：明确画风 + 线条 + 配色 + 背景
  - 文字渲染：提供设计上下文（"minimalist skincare brand logo" > "create a logo"）
  - 产品摄影：三点式柔光箱、具体角度、材质细节
  - 极简设计：单一主体定位、大面积留白、指定色调
  - 漫画分镜：风格流派 + 前后景分离 + 对话框布局

### 6. Nano Banana Pro 提示词技巧
- **URL**: https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/
- **内容**: 7 个针对 Nano Banana Pro 的提示词技巧
- **注意**: 页面 CSS 渲染问题可能影响抓取，建议浏览器访问

### 7. Gemini App 图像生成技巧
- **URL**: https://blog.google/products-and-platforms/products/gemini/image-generation-prompting-tips/
- **内容**: 面向终端用户的通用图像生成和编辑技巧
- **注意**: 同上，页面抓取可能不完整

### 8. Nano Banana 2 (Gemini 3.1 Flash Image)
- **URL**: https://deepmind.google/models/gemini-image/flash/
- **内容**: Nano Banana 2 的能力介绍（思考模式、高级文字渲染、Google 搜索 grounding）
- **关键要点**:
  - Thinking mode：复杂 prompt 通过"思考图像"逐步推理构图
  - 支持 4K 分辨率
  - 搜索 grounding：可基于实时数据生成图表/信息图

### 9. Vertex AI 图像生成 Prompt 指南
- **URL**: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/img-gen-prompt-guide
- **内容**: 企业级图像生成的 prompt 和属性指南

---

## 二级来源（社区/第三方，经验证质量较高）

### 10. Efficient Coder — Gemini Flash Image Prompting Guide
- **URL**: https://www.xugj520.cn/en/archives/gemini-2-5-flash-image-prompting-guide.html
- **内容**: 按图片类型分类的具体 prompt 示例（含完整 prompt 文本）
- **价值**: 提供了 6 个分类的完整 prompt 示例，可直接对照验证 Profile 建议

### 11. DataCamp — Gemini 2.5 Flash Image Complete Guide
- **URL**: https://www.datacamp.com/tutorial/gemini-2-5-flash-image-guide
- **内容**: 教程级别的完整指南（需登录访问）

### 12. eWeek — Best Nano Banana 2 Prompts 2026
- **URL**: https://www.eweek.com/news/best-nano-banana-2-prompts-gemini-3-1-flash-image/
- **内容**: Nano Banana 2 的 6 个最佳 prompt 实践

---

## 核心 Prompt 示例库（从官方来源提取）

以下示例经官方文档验证，可作为 Profile 优化的基准参考：

### 写实摄影
```
A photorealistic close-up portrait of an elderly Japanese ceramicist
in a rustic workshop, lit by golden hour sunlight, captured with an 85mm lens.
```

### 插画/贴纸
```
A kawaii-style sticker of a red panda wearing a bamboo hat, outlined in bold lines,
cel-shaded, vibrant colors, on a white background.
```

### 文字设计/Logo
```
A minimalist black-and-white logo for a coffee shop called 'The Daily Grind',
with a bold sans-serif font and a stylized coffee bean.
```

### 产品摄影
```
A high-resolution studio photograph of a matte black coffee mug on concrete,
lit with a three-point softbox, shot at 45°.
```

### 极简/负空间
```
A single red maple leaf in the bottom-right corner, off-white background,
soft lighting, square format.
```

### 漫画分镜
```
A noir-style comic panel: a trench-coated detective under a streetlamp in the rain,
caption: 'The city was a tough place to keep secrets.'
```

### 等距摄影
```
Make a photo that is perfectly isometric. It is not a miniature, it is a captured photo
that just happened to be perfectly isometric. It is a photo of a beautiful modern garden.
```

---

## 模型信息速查

| 代号 | 正式名称 | 定位 | 发布时间 |
|------|---------|------|---------|
| Nano Banana | Gemini 2.5 Flash Image | 速度优先，对话编辑 | 2025 |
| Nano Banana Pro | Gemini 3 Pro Image | 质量优先，复杂场景，文字渲染 | 2025.11 |
| Nano Banana 2 | Gemini 3.1 Flash Image | Pro 质量 + Flash 速度，思考模式，4K | 2026.02 |

---

## 更新日志

- **2026-04-03**: 补充语言相关官方来源，明确 Gemini/Nano Banana 与 Imagen 的语言支持差异
- **2026-03-06**: 初始创建，收录 10 个来源，提取核心示例库
