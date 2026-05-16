# Background Replacement Edit

Starter prompt template for replacing the background of an existing image while preserving the subject, pose, product geometry, visible text, and key edges.

## Use

```bash
/bananahub use background-replace-edit --input source.png
```

## Verified Models

- `gpt-image-2` — verified with `samples/sample-gpt-image-2-01.png` as a workflow preview board for the edit template.

## Supported Models

- `gpt-image-2` — recommended when provider edit support is available and subject-preservation constraints need strict wording.
- `gemini-3-pro-image-preview` — good fit for background replacement and natural scene integration.
- `gemini-3.1-flash-image-preview` — good faster option for simpler background swaps.
- `gpt-image-1` — compatible fallback through the `gpt-image` prompt variant.

## Sample Outputs

| File | Provider | Model | Prompt Variant | Notes |
|---|---|---|---|---|
| `samples/sample-gpt-image-2-01.png` | `chatgpt-compatible` | `gpt-image-2` | `gpt-image` | Workflow preview board showing the expected edit sequence: `Source`, `Replace background`, and `Preserve subject`. It is not a substitute for running the template with a real `--input` image. |

## Notes

- This template requires an input image for real edits.
- Do not treat background replacement as plain text-to-image generation when subject preservation matters.
- Use mask-capable providers for precise local edits when available.

## License

CC BY 4.0 unless this directory states otherwise.
