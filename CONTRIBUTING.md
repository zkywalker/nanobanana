# Contributing to bananahub-skill

## Scope

This repo contains both code and bundled template content:

- code, scripts, and general docs: MIT
- built-in templates under `references/templates/`: `CC-BY-4.0` unless a template directory says otherwise

## Commit sign-off

Sign off every commit with the Developer Certificate of Origin:

```bash
git commit -s -m "feat: your change"
```

By signing off, you certify that you have the right to submit the contribution under the applicable repo license.

## Template contributions

If a PR adds or edits a built-in template:

- set frontmatter `license` explicitly
- keep `author` and sample metadata accurate
- include only samples and copy that can be redistributed
- separate any code snippets or helper scripts from template content when they need a different license
