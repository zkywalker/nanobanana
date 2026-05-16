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

No sample image is checked in for this bundled starter template. The workflow is prompt- and schema-validated, with visual samples kept out of the skill package to keep installs lightweight.

## Sample Outputs

No sample outputs are included in this starter template. When adding samples in a remote template package, map each image to:

| Image | Model | Prompt |
|---|---|---|
| `samples/<image>.png` | `<model-id>` | `samples/<prompt>.md` |

## Notes

- Keep source summaries to 3–7 verified blocks.
- Lock exact module names before generation.
- Do not add samples here; heavy sample galleries belong in the remote BananaHub template library.

## License

CC BY 4.0 unless this directory states otherwise.
