---
created: 2026-05-15T00:00:00Z
command: generate
provider: chatgpt-compatible
requested_model: gpt-5.4
aspect_ratio: 16:9
template_id: repo-explainer-diagram
asset_type: repository-explainer
---

Design one repository explainer diagram for BananaHub Skill. Title text: "BananaHub Skill Architecture". Layout: left-to-right architecture diagram. The only block labels allowed are: "User", "/bananahub", "Prompt Pipeline", "Templates", "Provider Router", "Image Providers", "Outputs". Draw only these relationships: User -> /bananahub; /bananahub -> Prompt Pipeline; Prompt Pipeline -> Templates; Prompt Pipeline -> Provider Router; Provider Router -> Image Providers; Image Providers -> Outputs.

Verified source summary: BananaHub Skill exposes the /bananahub workflow for agents; prompt requests move through prompt optimization and template selection; configured provider profiles route work to image providers; outputs are saved images and reusable prompts/templates.

Style: modern product-doc architecture diagram, restrained colors, simple connectors, generous spacing, warm off-white background, banana-yellow and teal accents, dark readable text. Keep all labels large, high-contrast, and easy to read.

Do not add extra modules, paragraphs, fake file names, decorative code, fake screenshots, logos, watermarks, API keys, secret values, unsupported providers, tiny text, or invented relationships. Use only the exact title and exact block labels above.
