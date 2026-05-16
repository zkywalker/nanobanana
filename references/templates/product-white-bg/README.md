# E-commerce Product Clean Shot

Starter prompt template for clean ecommerce catalog product images with isolated subjects, realistic materials, and simple white backgrounds.

## Use

```bash
/bananahub use product-white-bg
```

## Verified Models

- `gemini-3.1-flash-image-preview` — verified with `samples/sample-3.1-flash-01.png` for a clean white-background headphone product shot.

## Supported Models

- `gpt-image-2` — recommended for high-fidelity product generation and strict avoidance of fake props or badges.
- `gemini-3-pro-image-preview` — good fit for polished materials and catalog lighting.
- `gemini-3.1-flash-image-preview` — good faster option for simple product shots.
- `gpt-image-1` — compatible fallback through the `gpt-image` prompt variant.

## Sample Outputs

| File | Provider | Model | Prompt Variant | Notes |
|---|---|---|---|---|
| `samples/sample-3.1-flash-01.png` | `google-ai-studio` | `gemini-3.1-flash-image-preview` | `gemini` | White-background over-ear headphone catalog shot. |

## Notes

- For real products, prefer edit/reference workflows over recreating the product from text.
- Manually verify logos, package text, and product geometry before publishing.

## License

CC BY 4.0 unless this directory states otherwise.
