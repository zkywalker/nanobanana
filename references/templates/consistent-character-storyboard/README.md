# Consistent Character Storyboard Workflow

A BananaHub workflow template for role-consistent storyboard exploration. It helps the agent lock one master character image, branch into contact-sheet or storyboard exploration, and iterate with single-variable edits instead of rewriting everything from scratch each round.

## Install

```bash
npx bananahub add bananahub-ai/banana-hub-skill/consistent-character-storyboard
```

## Verified Models

- `gemini-3-pro-image-preview` — verified with `samples/sample-3-pro-01.png` using the bundled Miso contact-sheet exploration sample

## Supported Models

- `gemini-3.1-flash-image-preview` — good default for fast exploration
- `gemini-3-pro-image-preview` — better fit when continuity and panel quality matter more than speed

## Sample Outputs

| File | Model | Prompt / Variant |
|---|---|---|
| `samples/sample-3-pro-01.png` | `gemini-3-pro-image-preview` | `3x3 contact sheet` exploration of the bundled Miso Siamese cat IP master reference |
