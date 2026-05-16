# Repository Explainer Diagram

Starter workflow for turning README excerpts, directory summaries, or code notes into one accurate project explainer diagram. It is bundled because repo-aware diagrams are a stable, high-frequency agent use case.

## Use

```bash
/bananahub use repo-explainer-diagram
```

## Supported Models

- Recommended: `gpt-image-2` for first-pass repo diagrams with strict labels and cleaner text.
- Gemini / Nano Banana: `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`
- OpenAI GPT Image fallback: `gpt-image-1`

## Verified Models

- `gemini-3-pro-image-preview` — verified with `samples/sample-3-pro-02.png` for a text-light template-flow diagram.

## Sample Outputs

| File | Provider | Model | Prompt Variant | Notes |
|---|---|---|---|---|
| `samples/sample-3-pro-02.png` | `google-ai-studio` | `gemini-3-pro-image-preview` | `gemini` | Legacy Nano Banana template-flow diagram with locked labels and simple connector structure. |

## Notes

- Keep source summaries to 3–7 verified blocks.
- Lock exact module names before generation.
- Keep the bundled sample count small; heavy sample galleries belong in the remote BananaHub template library.

## License

CC BY 4.0 unless this directory states otherwise.
