# Repository Explainer Diagram

Starter workflow for turning README excerpts, directory summaries, or code notes into one accurate project explainer diagram. It is bundled because repo-aware diagrams are a stable, high-frequency agent use case.

## Use

```bash
/bananahub use repo-explainer-diagram
```

## Model Coverage

- Recommended: `gpt-image-2` for first-pass repo diagrams with strict labels and cleaner text.
- Gemini / Nano Banana: `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`
- OpenAI GPT Image fallback: `gpt-image-1`

## Notes

- Keep source summaries to 3–7 verified blocks.
- Lock exact module names before generation.
- Do not add samples here; heavy sample galleries belong in the remote BananaHub template library.
