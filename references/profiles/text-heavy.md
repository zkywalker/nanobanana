# Profile: Text-Heavy Design (文字设计)

## Trigger Keywords

Logo、海报、名片、菜单、标牌、横幅、封面、标题、字体设计、排版、招牌、广告、宣传、传单、poster、banner、logo、typography、sign、cover、邀请函、贺卡、优惠券、证书

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### Text Handling (highest priority)
- All text intended to appear in the image must be wrapped in quotes
- Explicitly specify text position: centered, top, bottom, overlay
- Chinese text is preserved in original language by default (user wants Chinese displayed in the image)
- English text is preserved as-is
- Text exceeding 25 characters → warn and suggest shortening
- **Multi-line text**: describe each line separately with its own style and position:
  - "For the top line, the word '咖啡' in large bold serif. Below that, '每日新鲜烘焙' in smaller elegant script"
- **Text rendering accuracy**: bold serif fonts often render best in Gemini. Treat this as a rendering aid, not a universal design default; do not override the user's intended typography style

### Exact Copy Lock
- Treat user-provided text as exact copy, not inspiration
- Do not paraphrase slogans, translate display text, or invent filler microcopy
- If key title / subtitle / CTA text is missing or unstable, ask first in default mode
- Separate required text from optional decorative text; if optional text was not specified, leave it out

### Design Context (critical for quality)
- **Embed the brand identity or purpose when the user provides it** — context primes Gemini's design knowledge:
  - "A minimalist skincare brand logo" >> "create a logo"
  - "A rustic artisanal coffee shop storefront sign" >> "a coffee shop sign"
  - "A children's birthday party invitation" >> "an invitation"
- Include industry, tone, and target audience when the user provides them

### Typography Style
- No font specified → keep typography guidance generic unless the use case strongly implies a functional requirement
- Logo → bold, modern, distinctive letterforms
- Poster (海报) → large impactful typography, eye-catching
- Menu (菜单) → elegant, readable, well-organized
- Signage (标牌) → clear, high-contrast, legible at distance
- Invitation (邀请函) → elegant, refined, decorative
- Available font terms: serif, sans-serif, hand-lettered, brush script, monospace, slab serif, geometric sans-serif

### Contrast & Readability
- **Ensure high contrast between text and background** — this prevents the common failure mode where Gemini renders beautiful backgrounds but illegible text
- For text-over-image: "text clearly legible against the background, high contrast"
- For signs/banners: "text as the dominant visual element"
- Light text on dark background or dark text on light background — specify explicitly

### Visual Hierarchy
- Specify which text element is primary vs. secondary:
  - "Large bold title '老张咖啡' as the dominant element, smaller tagline '每日新鲜' below"
- For posters: Z-pattern layout (headline → image → body → CTA)
- For cards: centered hierarchy (title → content → details)

### Design Language
- No style specified → do not invent a full design language; only add broad functional constraints that improve readability
- Branding (品牌类) → clean, professional, modern design
- Event (活动类) → vibrant, energetic, festive
- Food & beverage (餐饮类) → warm, inviting, appetizing color scheme
- Tech (科技类) → sleek, minimalist, futuristic
- Luxury (奢侈品) → sophisticated, minimal, premium materials

### Layout & Composition
- Relationship between text and visual elements: text overlaying image, text beside illustration, text as the main visual
- Ensure breathing room: adequate white space around text elements

## Two-Step Method (Google's #1 Text Tip)

For designs with multiple text elements, use this two-step approach for significantly better accuracy:
1. **First**: discuss and finalize all text content with the user in conversation
2. **Then**: construct the image prompt with finalized text, each element described separately with position and style
3. This prevents text rendering errors that occur when Gemini processes complex text prompts in a single pass

## Example

**User input**: 做一个咖啡店的招牌，写着"老张咖啡"

**Base optimization**: Create a coffee shop sign with the text "老张咖啡"

**Enhanced result**: Create a coffee shop sign with the text "老张咖啡" as the dominant visual element, centered, clear high-contrast Chinese typography, clean signage-focused composition

## Model Recommendation

For text rendering scenarios, **automatically prefer `gemini-3-pro-image-preview` (Gemini 3 Pro Image)** unless the user specifies a different model. The Pro model is significantly better than Flash at text clarity and typographic accuracy.

## Aspect Ratio

- Poster → 3:4 or 2:3 (portrait)
- Banner/横幅 → 16:9 or wider
- Logo → 1:1
- Business card/名片 → 16:9 or 3:2
- Social media cover → varies by platform

## Behavioral Notes

- Text rendering is a Gemini Pro strength but can still produce errors; **always verify every character of rendered text after generation**, especially for Chinese text
- In-image text language is decided by the user — never translate it on your own
- Long text (e.g., full menu content) may render poorly; suggest splitting into separate generations
- Gemini supports multilingual text rendering — inform the user of this capability when relevant
- For Chinese text, keeping to 4-6 characters produces highest accuracy
- Do not invent brand tone, palette, materials, or decorative style unless the user gave enough context or confirmed the direction
- Missing copy is a clarification issue, not an invitation to write the copy yourself
- Write prompts in natural descriptive sentences, not tag lists
