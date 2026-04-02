# README Launch Visual Workflow

A BananaHub workflow template for converting README copy or product positioning into a launch-ready visual. It helps the agent lock one headline, one short support line, and one visual metaphor instead of letting the image drift into generic AI poster clutter.

## Install

```bash
npx bananahub add bananahub-ai/banana-hub-skill/readme-launch-visual
```

## Verified Models

- `gemini-3-pro-image-preview` — verified with `samples/sample-3-pro-01.png` and `samples/sample-3-pro-02.png` for homepage hero and OG cover variants

## Supported Models

- `gemini-3-pro-image-preview` — best fit when headline rendering and composition quality matter
- `gemini-3.1-flash-image-preview` — good option for faster concepting before refining the final hero

## Sample Outputs

| File | Model | Prompt / Variant |
|---|---|---|
| `samples/sample-3-pro-01.png` | `gemini-3-pro-image-preview` | Wide launch hero for `BananaHub` with the locked headline `Agent-native image workflows` and support line `Prompt optimization, templates, and editing in one flow` |
| `samples/sample-3-pro-02.png` | `gemini-3-pro-image-preview` | Wide OG-cover style launch visual with the locked headline `Build image workflows, not prompt piles` and a modular template-to-image card metaphor |
