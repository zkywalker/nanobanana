# BananaHub Discovery

Use this file when:

- the user explicitly asks Nano Banana to find, recommend, or browse templates
- the user invokes `discover ...`
- local template auto-matching is weak, but the task looks like a reusable prompt or workflow

## Discovery Surfaces

- **Local installed templates**: handled by `templates`, `use`, and Phase 2.1 in `references/optimization-pipeline.md`
- **Remote BananaHub catalog**: handled by `discover ...`

Keep these surfaces separate. Do not silently replace a good local match with a remote template search.

## Source Order

Use BananaHub's machine-readable files instead of scraping the visual homepage:

1. Read `https://nano-banana-hub.github.io/llms.txt` if you have not used BananaHub yet in the current conversation or if you need the latest entry-point guidance
2. Default to `https://nano-banana-hub.github.io/catalog-curated.json` for safer recommendations
3. Use `https://nano-banana-hub.github.io/catalog.json` when:
   - the user asks for more options or community templates
   - curated results are weak
   - the user explicitly says BananaHub / hub / community / discovered
4. Use `https://nano-banana-hub.github.io/agent-catalog.md` only as a readable summary when structured fields are not enough

Do not scrape cards or filters from the homepage when these files are available.

## Supported Commands

### `discover <request>`

Search BananaHub for matching templates.

- Default catalog: `catalog-curated.json`
- Return: top 3 candidates unless the user asks for more
- Use only frontmatter-level catalog fields for ranking:
  `id`, `type`, `title`, `title_en`, `description`, `tags`, `profile`, `difficulty`,
  `catalog_source`, `official`, `pinned`, `featured`, `install_cmd`, `template_url`

### `discover curated <request>`

Force curated-only search.

### `discover trending`

Show current trending templates. Prefer the BananaHub API or CLI trending output when available. Merge the trending IDs with catalog metadata before presenting results.

## Ranking Rules

Rank candidates in this order:

1. Strong relevance to the user's need: title, tags, description, profile
2. `pinned`
3. `featured`
4. `catalog_source: curated`
5. `official`
6. Stronger workflow fit when the user clearly needs a multi-step SOP

Keep the shortlist small. The goal is to reduce choice overload, not recreate the full gallery inside chat.

## Progressive Disclosure Rules

Remote discovery should stay lightweight:

1. Search and rank using the catalog only
2. Do **not** load the full remote template body during broad search
3. Load or inspect `template_url` only when:
   - the user asks to inspect a shortlisted candidate more closely
   - two candidates are too close to distinguish from catalog metadata alone
4. Install with the deterministic `install_cmd` from the catalog when available

## Install Flow

After recommending candidates:

1. Ask once whether to install the best match, inspect another shortlisted option, or continue without a template
2. If the user clearly says to install or directly use the best match, run the `install_cmd`
3. After installation, switch immediately into local activation:
   - prompt template → continue with `use <template-id>`
   - workflow template → continue with `use <template-id>` and guide step-by-step
4. Do not stop after installation unless the user explicitly wants to review first

## Default Presentation Format

Keep remote suggestions compact:

```text
BananaHub candidate templates
1. app-web-logo-system [workflow]
   Match: logo / brand / app icon
   Source: curated, official
   Install: bananahub add nano-banana-hub/nanobanana/app-web-logo-system

2. readme-launch-visual [workflow]
   Match: launch / hero / banner
   Source: curated, official
```

Then ask for one decision, not a long questionnaire.
