# Profile: Illustration (插画与漫画)

## Trigger Keywords

插画、漫画、动漫、卡通、手绘、二次元、Q版、赛博朋克风、像素画、扁平化、矢量、水彩画、油画、素描、涂鸦、anime、manga、cartoon、pixel art、comic

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### Art Style
- User mentions "动漫/二次元" → anime style / manga style
- User mentions "卡通" → cartoon illustration
- User mentions "手绘" → hand-drawn illustration
- User mentions "水彩" → watercolor painting
- **No explicit style → do not infer a specific style**; instead offer options during enhancement confirmation (e.g., anime / digital illustration / watercolor / cartoon) and let the user choose
- Never override a style the user has already specified

### Linework & Rendering Style
- Anime → clean lines, cel-shading
- Watercolor → soft edges, visible brushstrokes, wet-on-wet blending
- Sketch → pencil strokes, hatching, grayscale
- Pixel art → visible pixels, limited color palette, retro aesthetic

### Color Scheme
- No color scheme specified → infer reasonable default from art style
- Anime → vibrant colors (unless mood is dark)
- Watercolor → soft pastel tones
- Cyberpunk → neon colors, dark background
- Do not proactively restrict colors; only supplement when the style has a strong color tendency

### Background Treatment
- Character design / standing illustration → suggest simple clean background / white background
- Scene illustration → supplement environment details based on description
- Comic panel → describe panel layout if relevant

## Example

**User input**: 一个拿着魔法杖的小女巫

**Base optimization**: A little witch holding a magic wand

**Enhanced result (when user hasn't specified a style, offer options)**:
> 检测到插画类意图，但未指定画风。建议选择：
> 1. anime style — 日系动漫风
> 2. digital illustration — 数字插画
> 3. watercolor painting — 水彩风格
> 4. cartoon illustration — 欧美卡通

**After user selects anime**: A little witch holding a magic wand, anime style, vibrant colors, clean lines with cel-shading, simple gradient background, cheerful and whimsical mood

## Behavioral Notes

- Illustration styles are extremely diverse; when uncertain, prefer not adding a style keyword and let the user choose
- Never apply photographic lens language (85mm lens, bokeh) to illustrations
- Text in manga/anime is typically a visual element — preserve original language, do not translate
