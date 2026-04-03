# Repository Explainer Diagram Workflow

A BananaHub workflow template for turning real repository context into one clean explainer visual. It is built for agent workflows where the model should read README sections, local notes, or codebase summaries first, then compress them into a diagram with short exact labels.

## Install

```bash
npx bananahub add bananahub-ai/bananahub-skill/repo-explainer-diagram
```

## Verified Models

- `gemini-3-pro-image-preview` — verified with `samples/sample-3-pro-01.png` and `samples/sample-3-pro-02.png` for repository architecture and workflow explainer variants

## Supported Models

- `gemini-3-pro-image-preview` — best fit when label accuracy and layout clarity matter most
- `gemini-3.1-flash-image-preview` — good faster option for rough explainer drafts

## Sample Outputs

| File | Model | Prompt / Variant |
|---|---|---|
| `samples/sample-3-pro-01.png` | `gemini-3-pro-image-preview` | `BananaHub Architecture` left-to-right diagram using five locked blocks: GitHub Templates, BananaHub CLI, BananaHub Skill, Hub API, Catalog Site |
| `samples/sample-3-pro-02.png` | `gemini-3-pro-image-preview` | `BananaHub Template Flow` top-to-bottom workflow diagram using five locked blocks: User Request, Prompt Optimization, Profile Match, Template Suggestion, Generate or Edit |
