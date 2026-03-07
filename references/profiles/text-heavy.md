# Profile: Text-Heavy Design (文字设计)

## Trigger Keywords

Logo、海报、名片、菜单、标牌、横幅、封面、标题、字体设计、排版、招牌、广告、宣传、传单、poster、banner、logo、typography、sign、cover

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### Text Handling (highest priority)
- All text intended to appear in the image must be wrapped in quotes
- Explicitly specify text position: centered, top, bottom, overlay
- Chinese text is preserved in original language by default (user wants Chinese displayed in the image)
- English text is preserved as-is
- Text exceeding 25 characters → warn and suggest shortening

### Typography Style
- No font specified → infer from design type
- Logo → bold, modern, distinctive letterforms
- Poster (海报) → large impactful typography, eye-catching
- Menu (菜单) → elegant, readable, well-organized
- Signage (标牌) → clear, high-contrast, legible at distance

### Design Language
- No style specified → infer from purpose
- Branding (品牌类) → clean, professional, modern design
- Event (活动类) → vibrant, energetic, festive
- Food & beverage (餐饮类) → warm, inviting, appetizing color scheme
- Tech (科技类) → sleek, minimalist, futuristic

### Layout & Composition
- Relationship between text and visual elements: text overlaying image, text beside illustration, text as the main visual
- Ensure breathing room: adequate white space around text elements

## Example

**User input**: 做一个咖啡店的招牌，写着"老张咖啡"

**Base optimization**: Create a coffee shop sign with the text "老张咖啡"

**Enhanced result**: Create a coffee shop sign with the text "老张咖啡" prominently displayed, warm inviting color scheme, clean modern typography, wooden texture background, professional storefront signage design

## Model Recommendation

For text rendering scenarios, **automatically prefer `gemini-3-pro-image-preview` (Nano Banana Pro)** unless the user specifies a different model. The Pro model is significantly better than Flash at text clarity and typographic accuracy.

## Behavioral Notes

- Text rendering is a Gemini Pro strength but can still produce errors; suggest step-by-step verification for complex text
- In-image text language is decided by the user — never translate it on your own
- Long text (e.g., full menu content) may render poorly; suggest splitting into separate generations
- Gemini supports multilingual text rendering and translation switching — inform the user of this capability when relevant
