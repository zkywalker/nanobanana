# App and Web Logo Workflow

A BananaHub workflow template for generating app and web logos with platform-aware constraints. It is optimized for concept development where the model should first produce an icon-first mark that survives small sizes, then derive website and store variants from the same core idea.

## Install

```bash
npx bananahub add bananahub-ai/bananahub-skill/app-web-logo-system
```

## Best Practices

- Start from the most restrictive surface. For most teams that means the square app icon or favicon, not the full website lockup.
- Prefer icon-first exploration. App icons and favicons usually work better when they do not depend on long text.
- Keep one focal idea. The best platform guidance converges on a simple, recognizable mark with a strong silhouette.
- Ask Gemini for flat, centered, high-contrast symbols. Avoid mockups, scenes, glossy 3D effects, tiny details, and fake UI.
- Treat text as an exact lock. Only request initials or a wordmark when the copy is final and short enough to verify.
- Create variants on purpose: icon-only, wordmark, monochrome, and maskable or adaptive-icon versions should be separate passes.
- Review at small sizes early. If the mark fails at 16 to 32 pixels, simplify geometry before exploring style.
- Use BananaHub Skill for concept generation and controlled iteration, then finish the selected direction in vector tools.

## Platform Notes

- Apple app icons should stay simple, memorable, and focused on a single visual idea.
- Android adaptive icons need important content centered inside a safe area, because the system can mask the outer edges.
- Google Play listing icons should not bake in rounded corners, because the store applies its own shape treatment.
- PWA icons should include standard icon sizes and a maskable variant with enough inner safe area to survive different masks.

## Practical Checks

- Small-size test: shrink the icon to roughly 16 px, 32 px, and 48 px. If the idea collapses, remove detail before changing style.
- Android adaptive icon: Google documents a 108 x 108 dp foreground and background layer with the central 66 x 66 dp treated as the safe zone for important content.
- Google Play icon: prepare a 512 x 512 PNG asset and avoid relying on pre-rounded corners or heavy outer shadows.
- PWA installability: include at least 192 x 192 and 512 x 512 icons in the manifest.
- PWA maskable icon: keep the critical symbol inside the inner safe area; web.dev describes an 80 percent diameter safe circle for important content.
- Wordmark test: if the name is not still clean and verifiable at header size, keep the shipped app icon text-free and move the name to a separate website lockup.

## Prompt Heuristics

- Give Gemini brand context, not just the word "logo". A prompt like "a privacy-first finance app icon" is stronger than "make a logo".
- Keep prompts in natural sentences and keep the first generation short and constrained.
- Separate icon-only and wordmark generations into different passes.
- Use exact quotes for any initials or wordmark text that must render.
- Change one variable at a time: symbol, palette, typography, or padding.

## Verified Models

- `gemini-3-pro-image-preview` — bundled BananaHub brand-case sample in `samples/sample-3-pro-01.png`, showing the approved icon baseline plus a matching website lockup

The checked-in BananaHub sample is a worked example of the workflow after concept approval. The website lockup shown in the sample is a local deterministic derivative from the same approved mark, which matches the workflow rule to generate the icon idea first and derive locked variants second.

## Supported Models

- `gemini-3-pro-image-preview` — best fit when concept quality, exact short text, and geometric stability matter most
- `gemini-3.1-flash-image-preview` — good faster option for ideation and early variant exploration

## Sample Outputs

| File | Model | Notes |
|------|-------|-------|
| `samples/sample-3-pro-01.png` | `gemini-3-pro-image-preview` | BananaHub worked-example board: approved ringless app icon baseline plus a matching `BananaHub` website lockup derived from the same core mark |

## Sources

- Google Gemini API image generation docs: https://ai.google.dev/gemini-api/docs/image-generation
- Google DeepMind Gemini image prompt guide: https://deepmind.google/models/gemini-image/prompt-guide/
- Google Developers Blog prompt best practices: https://developers.googleblog.com/ja/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results
- Apple Human Interface Guidelines, App Icons: https://developer.apple.com/design/human-interface-guidelines/app-icons
- Android adaptive icon guidance: https://developer.android.com/guide/practices/ui_guidelines/icon_design_adaptive.html
- Google Play icon design specifications: https://developer.android.com/distribute/google-play/resources/icon-design-specifications
- MDN web app manifest icons: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest/Reference/icons
- web.dev maskable icons: https://web.dev/maskable-icon/
