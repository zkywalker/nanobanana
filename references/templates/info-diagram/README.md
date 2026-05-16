# Practical Infographic One-Pager

Starter prompt template for turning a short process, comparison, timeline, or framework into one readable infographic card.

## Use

```bash
/bananahub use info-diagram
```

## Verified Models

- `gemini-3.1-flash-image-preview` — verified with `samples/sample-3.1-flash-01.png` for a five-step coffee process infographic.

## Supported Models

- `gpt-image-2` — recommended when exact labels and strict text limits matter most.
- `gemini-3-pro-image-preview` — good fit for polished visual hierarchy and richer icons.
- `gemini-3.1-flash-image-preview` — good faster option for simple flow cards.
- `gpt-image-1` — compatible fallback through the `gpt-image` prompt variant.

## Sample Outputs

| File | Provider | Model | Prompt Variant | Notes |
|---|---|---|---|---|
| `samples/sample-3.1-flash-01.png` | `google-ai-studio` | `gemini-3.1-flash-image-preview` | `gemini` | Five-step coffee process infographic with locked step labels. |

## License

CC BY 4.0 unless this directory states otherwise.
