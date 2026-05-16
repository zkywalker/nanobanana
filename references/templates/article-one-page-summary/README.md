# Article One-Page Visual Summary

Starter workflow for turning an article, memo, transcript, or long note into one accurate visual summary. It is bundled because one-page knowledge cards are a common BananaHub use case.

## Use

```bash
/bananahub use article-one-page-summary
```

## Verified Models

- `gpt-image-2` — verified with `samples/sample-gpt-image-2-01.png` for a text-locked article summary infographic.

## Supported Models

- `gpt-image-2` — recommended when exact title, takeaway, and short labels matter most.
- `gemini-3-pro-image-preview` — good fit for rich layout exploration and polished one-page summaries.
- `gemini-3.1-flash-image-preview` — good faster option for early drafts.
- `gpt-image-1` — compatible fallback through the `gpt-image` prompt variant.

## Sample Outputs

| File | Provider | Model | Prompt Variant | Notes |
|---|---|---|---|---|
| `samples/sample-gpt-image-2-01.png` | `chatgpt-compatible` | `gpt-image-2` | `gpt-image` | Text-locked sample with title, takeaway, and the labels `Delegate`, `Review`, and `Orchestrate`. |

## Notes

- Read and compress the source before generation.
- Lock exact titles, labels, numbers, and claims before prompting.
- Treat the checked-in sample as a workflow preview, not a claim about a specific article.

## License

CC BY 4.0 unless this directory states otherwise.
