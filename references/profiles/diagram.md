# Profile: Diagram (图表与信息图)

## Trigger Keywords

图表、流程图、架构图、信息图、示意图、思维导图、组织架构、时间线、对比图、数据可视化、diagram、flowchart、infographic、chart、wireframe、blueprint

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### Layout / Organization
- Flow-based → flowchart with directional arrows, top-to-bottom / left-to-right layout
- Hierarchical → hierarchical tree structure, clear parent-child relationships
- Comparison → side-by-side comparison layout, clear visual separation
- Timeline → horizontal or vertical timeline with chronological markers
- Isometric → "clean 45-degree top-down isometric view, sharp angles, minimalist feel" (for conceptual/architectural diagrams)
- Hand-drawn explainer / sketchnote → explicit title area, central concept, grouped supporting regions, arrows or numbering to show reading order
- Unspecified → infer only when the content strongly implies one; otherwise keep layout guidance generic or ask

### Visual Theme
- If a visual theme is needed but the user did not specify one, a clean professional theme is a safe option; otherwise keep the theme generic
- Alternatives: corporate style, technical blueprint, hand-drawn sketch style, modern isometric infographic
- Always prioritize information clarity; minimize decorative elements

### Hand-Drawn Sketch Note Overlay
- Use when the user asks for 手绘笔记 / sketchnote / 白板风 / 草图说明 / 便签式讲解
- Do not force a white background, black ink linework, or accent colors unless the user asks for them or the subtype strongly implies them
- Prefer the safest transferable traits first: rough boxes, arrows, underlines, badges, handwritten-style labels, and visible reading order
- Break information into 3-6 key points; do not let the image become a dense wall of text
- Make layout zones explicit in the prompt: top title, central diagram, side notes, bottom summary
- Use simple icons or stick figures only if they help explain the concept; they are support elements, not the main subject

### Labels & Text
- Suggest clear, bold labels with readable font size
- Bold serif fonts tend to render most accurately in Gemini; sans-serif is appropriate for modern/tech aesthetics
- Labels within the diagram should stay in the user's language (Chinese labels remain Chinese)
- Key data points and titles should be prominently displayed
- **Wrap specific label text in quotes** for accurate rendering: `with labels "用户", "服务器", "数据库"`
- For hand-drawn notes, keep most labels to short phrases (ideally 2-8 Chinese characters) and avoid paragraph-length notes

### Content Lock
- Treat nodes, labels, sequence, grouping, and reading order as content constraints, not decoration
- If the diagram depends on exact labels or a specific step order, ask first in default mode
- Do not invent extra boxes, services, metrics, or arrows just to make the diagram feel "complete"
- When the user gives a partial list, prefer a simpler diagram over speculative expansion

### Color Palette
- Only specify a color scheme when differentiation or readability requires it
- Professional color palette with 3-5 distinct colors for differentiation
- Avoid overly vibrant or artistic color schemes
- For hand-drawn notes, only specify accent colors when color coding is important to the explanation or the user asked for a notebook / whiteboard / marker look

### Element Count (important)
- **Keep diagrams to 5-8 elements maximum** for reliable results — Gemini degrades with complex diagrams (labels overlap, arrows cross, layout breaks)
- If the user's diagram requires more elements, suggest breaking it into multiple simpler diagrams
- Enumerate specific components when possible: "showing these services: API Gateway, User Service, Order Service, Payment Service, and Database"

## Infographic vs. Technical Diagram

These are different sub-categories with different needs:

### Technical Diagram (flowchart, architecture, etc.)
- Prioritize: structural accuracy, clear relationships, readable labels
- Style: clean, minimal, professional
- Warning: always remind user to verify connections and labels

### Infographic (data visualization, educational, editorial)
- Prioritize: visual storytelling, narrative flow, design appeal
- Style: can be more visually rich — icons, illustrations, color-coded sections
- May combine text, data, and visual elements — treat like a blend of diagram + text-heavy
- For infographics, suggest isometric style or flat design for modern appeal

### Hand-Drawn Infographic / Explainer
- Best for: process explanations, concept summaries, study notes, project introductions, side-by-side comparisons
- Prompt explicitly for reading flow: "top title, left-to-right steps, small supporting notes around the main diagram"
- Use educational phrasing rather than cinematic phrasing
- If the user wants Chinese output, keep labels in Chinese and limit total text load

## Two-Step Method (for text-heavy diagrams)

For diagrams with many labels, use this approach for better text accuracy:
1. First discuss and finalize all text labels/content with the user in conversation
2. Then construct the image prompt with all labels explicitly listed
3. This significantly reduces text rendering errors

## Example

**User input**: 画一个微服务架构图

**Base optimization**: Create a microservices architecture diagram

**Enhanced result**: Create a microservices architecture diagram showing these services: "API Gateway", "User Service", "Order Service", "Payment Service", and a shared "PostgreSQL Database", hierarchical layout with clear service boundaries, directional arrows showing request flow, clear readable labels

## Model Recommendation

- **Technical diagrams with many labels** → prefer Gemini 3 Pro Image for text rendering accuracy
- **Diagrams requiring factual/real-world data** → mention that Gemini can leverage its knowledge base for known patterns (e.g., "standard microservices with API gateway pattern")

## Behavioral Notes

- **Never add artistic modifiers** (lighting, atmosphere, depth of field — these are irrelevant to diagrams)
- Diagram text content requires accuracy; do not fabricate labels the user didn't mention
- **Always remind the user: AI-generated diagram data may be inaccurate — verify factual content**
- For complex diagrams (>8 nodes), suggest using dedicated tools (Mermaid, draw.io); Gemini is better suited for conceptual diagrams and infographics
- You may reference real-world concepts, technical terms, or known architecture patterns in the prompt to leverage Gemini's knowledge base
- Encourage users to list specific elements/nodes they want shown — the more explicit, the more accurate
- Hand-drawn style is an overlay on top of diagram structure; never let the decorative sketch aesthetic override the actual information hierarchy
- When uncertain, prefer keeping only the layout and linework cues of a hand-drawn explainer; do not add background or palette constraints on your own
- If exact structure matters more than aesthetics, ask for the node list and reading order before optimizing style
