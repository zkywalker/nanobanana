# BananaHub — Project Planning Document

> This is a human-facing planning document for the BananaHub template ecosystem.
> For agent-consumable references, see `references/template-system.md` and `references/template-format-spec.md`.

**Version**: 0.1.0 | **Status**: In Progress | **Date**: 2026-03-24

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    BananaHub Ecosystem                    │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Template  │  │ CLI Tool │  │ Creator  │  │  Hub    │ │
│  │  Format   │  │(bananahub│  │  Skill   │  │  Site   │ │
│  │          │  │   CLI)   │  │          │  │         │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │              │             │              │      │
│       └──────────────┴─────────────┴──────────────┘      │
│                          │                                │
│                   GitHub Repos                            │
│              (decentralized storage)                      │
└─────────────────────────────────────────────────────────┘
```

**Design principles**:
- Decentralized: templates live in author's own GitHub repos
- Self-describing: template.md frontmatter contains all metadata
- Progressive disclosure: auto-suggest matching templates, don't force
- Zero config: `npx bananahub add user/repo` and done
- AI-native: creator skill lets AI help users build templates

---

## CLI Tool: `bananahub`

**Package**: `bananahub` on npm | **Language**: Node.js (ESM) | **Source**: `/home/coder/project/bananahub/`

### Commands

```bash
# Install
npx bananahub add <user/repo>                    # Install single-template repo
npx bananahub add <user/repo> --template <name>  # Install specific template from multi-repo
npx bananahub add <user/repo> --all              # Install all templates from multi-repo

# Manage
npx bananahub remove <template-id>               # Uninstall a template
npx bananahub list                                # List installed templates
npx bananahub update [template-id]                # Update one or all templates
npx bananahub info <template-id>                  # Show template details

# Discover
npx bananahub search <keyword>                    # Search hub for templates
npx bananahub trending                            # Show trending templates

# Utility
npx bananahub init                                # Initialize a new template repo (scaffolding)
npx bananahub validate [path]                     # Validate template.md format
npx bananahub registry rebuild                    # Rebuild local .registry.json
```

### `add` Flow

1. **Resolve repo**: fetch repo info via GitHub API
2. **Detect type**: root `template.md` (single) or `bananahub.json` (multi)
3. **Download**: GitHub tarball API → extract to temp dir
4. **Validate**: parse frontmatter, check required fields, validate samples
5. **Install**: copy to `~/.config/nanobanana/templates/<id>/`
6. **Write .source.json**: record provenance
7. **Rebuild registry**: regenerate `.registry.json`
8. **Report install**: POST to hub API (fire-and-forget)

### `init` Scaffolding

Interactive prompts → generates:
```
my-template/
├── template.md     # Pre-filled frontmatter + placeholder sections
├── samples/
│   └── .gitkeep
└── README.md
```

### Install Count Tracking

**Mechanism**: on each `add`, CLI POSTs to hub API:
```
POST https://bananahub-api.workers.dev/api/installs
{ "repo": "user/repo", "template_id": "cyberpunk-city", "cli_version": "0.1.0" }
```

**Backend**: Cloudflare Worker + KV (free tier: 100K reads/day, 1K writes/day)
**Privacy**: no user identification, no IP logging, only repo + template_id + timestamp

**Hub reads**:
```
GET /api/stats?repo=user/repo → { "total_installs": 42, "weekly_installs": 7 }
GET /api/trending → [{ "repo": "...", "installs_7d": 15 }, ...]
```

---

## Hub Site: bananahub.github.io

### Architecture

```
Static site (GitHub Pages)
├── index.html                # Main page: search, browse, trending
├── template/{id}.html        # Template detail pages (generated)
├── assets/
│   ├── css/
│   └── js/
│       ├── app.js            # Client-side rendering
│       └── api.js            # Hub API client
└── data/
    └── catalog.json          # Aggregated template catalog (built by GitHub Action)
```

### Data Flow

1. Template authors submit repo URL via PR to `catalog-source.json`
2. GitHub Action (daily): fetches each repo's `template.md`, extracts frontmatter + sample URLs, builds `catalog.json`
3. Static site reads `catalog.json` + images from `raw.githubusercontent.com`
4. Install counts from Cloudflare Worker API

### catalog-source.json

```json
{
  "repos": [
    "user-a/nanobanana-cyberpunk",
    "user-b/nanobanana-templates",
    "nanobanana/official-templates"
  ]
}
```

### catalog.json (Built Artifact)

```json
{
  "generated_at": "2026-03-24T00:00:00Z",
  "templates": [
    {
      "id": "cyberpunk-city",
      "title": "赛博朋克城市夜景",
      "title_en": "Cyberpunk City Nightscape",
      "description": "一键生成赛博朋克风格的城市夜景",
      "author": "user-a",
      "repo": "user-a/nanobanana-cyberpunk",
      "profile": "photo",
      "tags": ["赛博朋克", "城市", "夜景"],
      "difficulty": "beginner",
      "models": [{ "name": "gemini-3-pro-image-preview", "quality": "best" }],
      "samples": [{
        "url": "https://raw.githubusercontent.com/user-a/nanobanana-cyberpunk/main/samples/sample-01.jpg",
        "model": "gemini-3-pro-image-preview",
        "prompt": "Cyberpunk city street at night..."
      }],
      "install_count": 42,
      "version": "1.0.0"
    }
  ]
}
```

### Site Features

| Feature | Description |
|---------|-------------|
| **Browse** | Grid of template cards with sample image, title, tags, install count |
| **Search** | Client-side search by title, tags, description (bilingual) |
| **Filter** | By profile, difficulty, model support |
| **Sort** | By installs (trending), date (newest), name |
| **Detail page** | Full template info: samples with model/prompt, variables, install command |
| **Install button** | Copy `npx bananahub add user/repo` to clipboard |
| **Submit** | Link to open PR on catalog repo |
| **Leaderboard** | Top templates by install count (all-time, weekly) |

### Template Card UI

```
┌─────────────────────────────┐
│  [sample-01.jpg preview]    │
│                             │
│  赛博朋克城市夜景            │
│  Cyberpunk City Nightscape  │
│                             │
│  📷 photo  ⭐ beginner      │
│  🏷️ 赛博朋克 城市 夜景      │
│                             │
│  by user-a  📥 42 installs  │
│  Models: Pro ✅ Flash ✅     │
│                             │
│  [Copy Install Command]     │
└─────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Foundation ✅
- [x] Template format definition (template.md spec)
- [x] Built-in example templates (5 templates, validated against best practices)
- [x] SKILL.md command routing (templates, use, create-template)
- [x] Auto-matching logic in Phase 2.1
- [x] Creator skill flow
- [x] Dual search path (built-in + installed)
- [x] .registry.json auto-generation
- [x] Agent-friendly doc structure (three-tier progressive loading)
- [ ] Generate actual sample images for built-in templates

### Phase 2: CLI Tool ✅
- [x] npm package `bananahub` initialized
- [x] `add` command (GitHub tarball → install → track)
- [x] `remove`, `list`, `update`, `info` commands
- [x] `init` scaffolding
- [x] `validate` format checking
- [x] `search` / `trending` (placeholder for hub API)
- [ ] Publish to npm

### Phase 3: Hub Backend
- [ ] Cloudflare Worker: install count API
- [ ] Cloudflare KV: store install counts per repo/template
- [ ] API endpoints: POST /installs, GET /stats, GET /trending
- [ ] Rate limiting and basic validation

### Phase 4: Hub Site
- [ ] Static site scaffold (HTML/CSS/JS, GitHub Pages)
- [ ] catalog-source.json submission flow
- [ ] GitHub Action: build catalog.json from source repos
- [ ] Template card grid with search/filter
- [ ] Template detail pages
- [ ] Leaderboard / trending section
- [ ] Mobile responsive design

### Phase 5: Polish
- [ ] Template versioning and update notifications
- [ ] Template collections / curated lists
- [ ] User profiles (link to GitHub)
- [ ] Comments / ratings (via GitHub Discussions?)
- [ ] i18n (Chinese + English site)

---

## Future Repos

| Repo | Purpose | Status |
|------|---------|--------|
| `bananahub` (npm) | CLI tool | ✅ Built at `/home/coder/project/bananahub/` |
| `bananahub.github.io` | Hub static site | Planned |
| `bananahub-api` | Cloudflare Worker for install tracking | Planned |
| `nanobanana-official-templates` | Official template collection | Planned |

## Open Questions

1. **Hub domain**: `bananahub.github.io` or custom domain?
2. **Multi-model samples**: require samples from multiple models, or 1 enough?
3. **Template review**: approval process for hub submissions, or accept all valid?
4. **Offline mode**: CLI work without network (skip tracking, use cached search)?
