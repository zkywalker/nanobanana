# Nano Banana Prompt Optimization Guide

This document defines the rules for the base optimization phase. For enhancement rules, see the Profile files in `profiles/`.

## Error Detection Rules (used during base optimization)

When optimizing a user prompt, check for and fix the following common issues:

### 1. Keyword List Pattern
**Detect**: comma-separated keyword dumps, e.g., "cat, window, sunlight, cozy"
**Fix**: rewrite as natural language: "A cat sitting by a window in warm sunlight, creating a cozy atmosphere"

### 2. SD/Midjourney Weight Syntax
**Detect**: bracket weights like `(detailed:1.5)`, `[negative]`, `{emphasis}`
**Fix**: remove all weight syntax. Express emphasis through descriptive language instead.

### 3. Negative Phrasing
**Detect**: "no blur", "without distortion", "not ugly", etc.
**Fix**: restate positively: "sharp focus", "clean lines", "beautiful"

### 4. Buried Subject
**Detect**: subject appears after modifiers or scene descriptions
**Fix**: move subject to the beginning of the prompt

### 5. Quality Tag Spam
**Detect**: "masterpiece, best quality, ultra detailed, 8k, HDR", etc.
**Fix**: delete. Nano Banana does not use quality tags. Describe the actual desired visual effect instead.

### 6. In-Image Text Too Long
**Detect**: requested render text exceeds 25 characters
**Handle**: warn user that short phrases render best; suggest splitting or shortening.

## Smart Translation Rules

### Descriptive Text → Translate to English
User's description of the scene content — translate into natural English (not literal; rewrite to suit Nano Banana's style).

### In-Image Text → Preserve Original Language
Text the user wants displayed in the image — preserve in original language, wrapped in quotes.

**Signals for recognizing in-image text**:
- Content wrapped in quotes: `"生日快乐"`
- Content following "写着/印着/显示/标注/刻着"
- Brand names, slogans, labels, or other text explicitly meant to appear in the image

**Examples**:
| Input | Translation Result |
|-------|-------------------|
| 写着"春天来了"的横幅 | a banner with the text "春天来了" |
| T恤上印着"HELLO" | a T-shirt with "HELLO" printed on it |
| 一个红色的苹果 | a red apple |
| 咖啡杯上写着"Good Morning" | a coffee cup with "Good Morning" written on it |

## Structuring Rules

1. **Subject first**: ensure the image subject is at the beginning of the prompt
2. **Trigger prefix**: add "Create an image of" or another suitable action phrase (Generate, Draw, Paint, etc., chosen based on content)

## Intent Recognition Keyword Table

| Profile | Trigger Keywords |
|---------|-----------------|
| `photo` | 照片、写实、人像、肖像、风景、街拍、产品图、美食摄影、纪实、抓拍、摄影、真实感、photo、portrait、landscape |
| `illustration` | 插画、漫画、动漫、卡通、手绘、二次元、Q版、赛博朋克风、像素画、扁平化、矢量、水彩画、油画、素描、涂鸦、anime、manga、cartoon、pixel art、comic |
| `diagram` | 图表、流程图、架构图、信息图、示意图、思维导图、组织架构、时间线、对比图、数据可视化、diagram、flowchart、infographic、chart |
| `text-heavy` | Logo、海报、名片、菜单、标牌、横幅、封面、标题、字体设计、排版、招牌、广告、宣传、传单、poster、banner、logo、typography |
| `minimal` | 极简、留白、壁纸、背景图、纯色、简约、负空间、桌面壁纸、手机壁纸、抽象、纹理、minimal、wallpaper、abstract、texture |
| `general` | No match to any of the above categories |

**Recognition priority**: keyword direct match > semantic inference > fall back to general

## Aspect Ratio Recommendations

| Scene | Recommended Ratio |
|-------|-------------------|
| Portrait / character (人像/角色) | 3:4 or 9:16 |
| Landscape / panorama (风景/全景) | 16:9 or 3:2 |
| Square / social media (正方形/社交媒体) | 1:1 |
| Product / still life (产品/静物) | 1:1 or 4:3 |
| Cinematic (电影感) | 16:9 |
| Phone wallpaper (手机壁纸) | 9:16 |
| Desktop wallpaper (桌面壁纸) | 16:9 |

## Model Reference

### gemini-3-pro-image-preview (Nano Banana Pro)
- **Best for**: high quality, rich detail, complex scenes, text rendering
- **Aspect ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3
- **Recommendation**: default model

### gemini-2.0-flash-preview-image-generation (Nano Banana Flash)
- **Best for**: fast generation, simple scenes, rapid iteration
- **Aspect ratios**: 1:1, 16:9, 9:16, 4:3, 3:4
- **Trade-off**: faster but slightly lower quality than Pro
