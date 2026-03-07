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
- Unspecified → infer the most suitable layout from content

### Visual Theme
- Default suggestion: clean minimalist design, professional appearance
- Alternatives: corporate style, technical blueprint, hand-drawn sketch style
- Always prioritize information clarity; minimize decorative elements

### Labels & Text
- Suggest clear sans-serif labels, readable font size
- Labels within the diagram should stay in the user's language (Chinese labels remain Chinese)
- Key data points and titles should be prominently displayed

### Color Palette
- Default suggestion: limited, distinguishable color scheme
- Professional color palette with 3-5 distinct colors for differentiation
- Avoid overly vibrant or artistic color schemes

## Example

**User input**: 画一个微服务架构图

**Base optimization**: Create a microservices architecture diagram

**Enhanced result**: Create a microservices architecture diagram, clean minimalist design, hierarchical layout with clear service boundaries, directional arrows showing data flow, professional color palette with distinct colors for each service layer, clear sans-serif labels

## Behavioral Notes

- **Never add artistic modifiers** (lighting, atmosphere, depth of field — these are irrelevant to diagrams)
- Diagram text content requires accuracy; do not fabricate labels the user didn't mention
- **Always remind the user: AI-generated diagram data may be inaccurate — verify factual content**
- For complex diagrams, suggest using dedicated tools (Mermaid, draw.io); Gemini is better suited for conceptual diagrams
- You may reference real-world concepts, technical terms, or known architecture patterns (e.g., "microservices with API gateway pattern") in the prompt to leverage Gemini's knowledge base for improved accuracy
