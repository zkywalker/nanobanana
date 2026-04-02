# Profile: Product Photography (产品摄影)

## Trigger Keywords

产品图、商品、电商、淘宝、主图、白底图、product shot、产品摄影、目录图、catalog、商品展示、产品展示

## Enhancement Dimensions

After base optimization, check and fill in the following dimensions as needed (only add what the user hasn't mentioned):

### Lighting Setup (highest impact)
- Use explicit lighting setup only when the user asks for a studio/commercial look or when the product-shot context strongly implies it
- White background product → "clean even studio lighting, minimal shadows, bright white backdrop"
- Luxury/premium → "dramatic side lighting with deep shadows, dark moody background"
- Food product → "warm appetizing lighting, slight backlight to create glow" (defer to photo profile's food guidance for full food styling)
- Skincare/cosmetics → "soft diffused lighting, clean clinical aesthetic"

### Camera Angle
- Do not force a camera angle unless the user asked for one or the platform/use case strongly implies it
- Available angles:
  - Hero angle (45°) → standard product shot, shows top and front
  - Flat lay (90° overhead) → good for collections, accessories, food
  - Eye-level (0°) → bottles, packaging, shoes
  - Low angle (below eye level) → makes product look imposing/premium
- Multiple products → "arranged in a grid layout" or "artfully scattered flat lay"

### Surface & Background
- No background specified → do not invent a surface/background unless the user mentions a use case that implies it:
  - E-commerce/catalog → "clean white background, isolated product"
  - Lifestyle → "styled on a [appropriate surface]: marble countertop, rustic wooden table, linen fabric"
  - Premium → "on a matte black surface" or "on polished dark stone"
- Surface material affects perceived quality — match surface to product tier

### Material & Texture Rendering
- Explicitly describe the product's key materials for maximum realism:
  - Glass → "transparent glass with refraction and caustics"
  - Metal → "brushed stainless steel with subtle reflections" or "polished chrome"
  - Fabric → "soft cotton texture, visible weave pattern"
  - Plastic → "glossy injection-molded plastic" or "matte soft-touch finish"
  - Leather → "genuine leather with natural grain texture"
  - Wood → "natural wood grain, warm honey-toned finish"
- Focus on the 1-2 most prominent materials; do not list every material

### Brand Context
- When the user describes a brand or product purpose, embed that context:
  - "minimalist skincare brand" > "skincare product"
  - "artisanal coffee roaster" > "coffee bag"
  - "premium tech accessory" > "phone case"
- Brand context primes Gemini's design knowledge for appropriate styling

### Platform / Use-Case Lock
- Treat platform and usage context as constraints when the user mentions them: 淘宝主图, 亚马逊目录图, 小红书封面, 官网 banner, packaging mockup
- If the platform is not specified, do not assume white background, square ratio, or listing-style composition
- If packaging text, logo, or product colorway is not specified, do not invent it
- When the output format depends heavily on the platform, ask first in default mode

## Example

**User input**: 一个白底的蓝牙耳机产品图

**Base optimization**: A Bluetooth headphone product photo on a white background

**Enhanced result**: Create a photorealistic product shot of Bluetooth headphones on a clean white background, even studio lighting, sharp focus on product details, isolated composition, catalog photography style

## Model Recommendation

Product photography benefits from high detail — **prefer `gemini-3-pro-image-preview` (Gemini 3 Pro Image)** for material fidelity and accurate text rendering on packaging.

## Aspect Ratio

- Single product → 1:1 (standard for e-commerce platforms)
- Product in context/lifestyle → 4:3 or 3:2
- E-commerce main image (淘宝主图) → 1:1

## Behavioral Notes

- Product photography is NOT artistic photography — prioritize clarity, accuracy, and commercial appeal over artistic expression
- Do not add mood/atmosphere unless the user requests lifestyle-style shots
- White background products need even, shadow-free lighting — do not add dramatic lighting by default
- For e-commerce, 1:1 ratio and white background are good suggestions, but do not inject them unless the platform/use case is explicit or the user confirms
- When user mentions a specific platform (淘宝、小红书、亚马逊), adjust styling to match that platform's conventions
- Material descriptions are useful when the material is central to the product; do not guess materials the user did not imply
