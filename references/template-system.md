# Template System

Nanobanana includes a prompt template ecosystem — curated, reusable prompt recipes with variable slots, sample images, and model annotations. Templates support progressive disclosure: auto-suggested when context matches, or explicitly invoked.

## Template Search Paths

Templates are loaded from two locations (merged). On ID conflict, user-installed wins:

1. **Built-in** (shipped with skill): `~/.claude/skills/nanobananaskill/references/templates/`
2. **User-installed** (via `npx bananahub add`): `~/.config/nanobanana/templates/`

Each path contains template directories and an auto-generated `.registry.json` index.

## Template File Format

Templates are agent-consumed documents. They follow a two-tier progressive disclosure model:

```
Tier 1 — Frontmatter (always parsed for listing/matching, ~50 tokens)
  id, title, profile, tags, models, aspect, difficulty
  → used by: templates list, auto-matching, BananaHub catalog

Tier 2 — Body (loaded only when template is activated via `use`, ~200-500 tokens)
  Prompt Template, Variables table, Tips
  → used by: prompt assembly, variable resolution
```

### Frontmatter (Tier 1 — Discovery)

Required fields for listing and auto-matching:

| Field | Purpose | Example |
|-------|---------|---------|
| `id` | Unique identifier (lowercase, hyphens, 3-50 chars) | `cyberpunk-city` |
| `title` | Chinese display title for listing | `赛博朋克城市夜景` |
| `title_en` | English display title | `Cyberpunk City Nightscape` |
| `author` | GitHub username | `nanobanana` |
| `version` | Semver | `1.0.0` |
| `profile` | Target enhancement profile | `photo` |
| `tags` | Bilingual keywords for search + auto-matching | `[赛博朋克, 城市, cyberpunk, neon]` |
| `models` | Tested models with quality rating (best/good/ok) | see below |
| `aspect` | Recommended aspect ratio | `"16:9"` |
| `difficulty` | Target user level | `beginner` / `intermediate` / `advanced` |
| `samples` | Sample image metadata (file, model, prompt) | see below |
| `created` / `updated` | ISO dates | `2026-03-24` |

### Body (Tier 2 — Activation)

Body sections must follow this exact order for consistent agent parsing:

1. **`## Prompt Template`** — the core prompt with `{{variable|default}}` slots inside a code block
2. **`## Variables`** — pipe table mapping each variable to its default and description
3. **`## Tips`** — bullet list of concrete, actionable tips (no vague advice)

### Body Authoring Constraints

These rules ensure templates are effective for both AI agents and Gemini image generation:

| Rule | Rationale |
|------|-----------|
| **Total body < 100 lines** | Keeps Tier 2 token cost low when template is activated |
| **Prompt Template < 80 words** | Gemini quality degrades with overly long prompts; 30-80 words is optimal |
| **3-6 variables per template** | Too few = not customizable; too many = confusing for beginners |
| **Variables use snake_case** | Consistent naming for agent parsing |
| **Each `{{var}}` has a default** | Templates must work with zero user input |
| **Defaults are complete sentences/phrases** | Gemini understands narrative language better than keyword fragments |
| **No "8K", "ultra-detailed", "masterpiece"** | These are SD/MJ quality tags; they don't improve Gemini output |
| **Use "photorealistic" for photo profile** | Google's official style anchor for realistic images |
| **Tips are specific and testable** | "Use deep focus for cityscapes" not "experiment with different settings" |
| **Tags include both Chinese and English** | Enables auto-matching from Chinese user input AND English search |

### Variable Syntax

`{{name|default_value}}` — double braces, snake_case name, pipe separator, fallback value.

- `{{scene|rain-soaked alley}}` — with default
- `{{subject}}` — without default (must be provided by user)

Full format spec: `references/template-format-spec.md`

## `templates` — List All Templates

1. Scan both template search paths for `.registry.json` (or rebuild by scanning directories)
2. Merge results (user-installed wins on ID conflict)
3. Group by `profile`, display:

```
📦 可用模板 (N 个)

📷 写实摄影 (photo)
  cyberpunk-city        赛博朋克城市夜景        ⭐ beginner

😀 贴纸表情包 (sticker)
  cute-sticker          Q版贴纸表情包           ⭐ beginner

🛍️ 产品摄影 (product)
  product-white-bg      电商白底产品图          ⭐ beginner

📊 图表信息图 (diagram)
  info-diagram          信息图/流程图           ⭐⭐ intermediate

🎨 极简留白 (minimal)
  minimal-wallpaper     极简手机壁纸            ⭐ beginner

用法: /nanobanana templates <name>  查看详情
      /nanobanana use <name> [描述]  使用模板生成
      /nanobanana create-template    创建新模板
安装更多: npx bananahub search <关键词>
```

Profile icon mapping: photo→📷, illustration→🎨, diagram→📊, text-heavy→📝, minimal→🎨, sticker→😀, 3d→🧊, product→🛍️, concept-art→🖼️, general→📋

## `templates <name>` — Show Template Details

1. Search both template paths for `<name>/template.md`
2. Parse frontmatter and body
3. Display: title, description, prompt template with variable highlights, variable table, supported models with quality ratings, recommended aspect ratio, tips
4. If `samples` entries exist in frontmatter, show sample image paths (user can view with Read tool)
5. End with usage hint: `/nanobanana use <name>` or `/nanobanana use <name> <自定义描述>`

## `use <template-id> [自定义描述]` — Generate from Template

1. **Locate template**: search both template paths for `<id>/template.md`
2. **Read template**: parse frontmatter + Prompt Template section
3. **Extract variables**: find all `{{variable|default}}` slots
4. **Apply user input**:
   - If no user description → use all default values, filling each `{{var|default}}` with `default`
   - If user provides a description → analyze intent, map to relevant variables, replace matching ones while keeping unmentioned at defaults
   - Apply smart translation (Phase 1 rules) to user-provided Chinese descriptions before inserting
5. **Apply template parameters**: use template's `aspect` and first `quality: best` model as defaults (unless user provides `--aspect` or `--model` flags)
6. **Generate**: follow standard Image Generation Flow — build command, execute script, display result
7. **Display template attribution**:
   ```
   ✅ 图片已生成 (模板: cyberpunk-city)
   📁 路径: [file_path]
   🔧 模型: [model] | 宽高比: [ratio] | 尺寸: [WxH]
   📝 使用的 Prompt: [final assembled prompt]
   🎨 模板: cyberpunk-city v1.0.0 by author-name
   ```

## Template Variable Resolution

When matching user descriptions to template variables:

1. **Direct mapping**: if user mentions a concept that clearly maps to a variable, replace it
   - User: "东京街头" → `scene` = "Tokyo street with traditional izakaya signs"
   - User: "紫色和金色" → `colors` = "purple and gold"
2. **Partial override**: only replace variables the user mentioned; keep others at defaults
3. **Full override**: if user provides a complete scene description that doesn't fit variable slots, treat the assembled prompt as a starting point and blend user intent
4. **Conflict resolution**: user's explicit choices always override template defaults

## `create-template` — AI-Guided Template Creation

When the user invokes `create-template`, guide them through creating a new template in 4 phases.

**The output template.md MUST conform to the Body Authoring Constraints above.** Specifically:
- Body < 100 lines total
- Prompt Template < 80 words (30-80 word sweet spot for Gemini)
- 3-6 variables with snake_case names and complete-sentence defaults
- No SD/MJ quality tags ("8K", "ultra-detailed", "masterpiece")
- Use narrative sentence structure, not comma-separated keyword lists
- Tips must be specific and testable, not vague
- Tags bilingual (Chinese + English) with ≥ 3 tags

### Phase 1: Intent Gathering

Ask the user (combine questions when possible):
1. "这个模板用来生成什么类型的图片？" → determine profile
2. "描述一下你想要的图片效果" → extract core prompt structure
3. "哪些部分应该是可以自定义的？" → identify variable slots
4. "目标用户是谁？新手还是有经验的？" → difficulty level

If the user provides a description upfront (e.g., `create-template 水墨山水画`), extract as much as possible before asking follow-ups.

### Phase 2: Prompt Drafting

1. Draft an English prompt template based on user intent
2. Insert `{{variable|default}}` for customizable parts
3. Present to user for review:
   ```
   📝 Prompt 模板草稿:

   Traditional Chinese ink wash painting of {{subject|misty mountains with pine trees}},
   {{style|sumi-e brushwork with wet-on-wet technique}},
   {{atmosphere|ethereal morning fog rising from valleys}},
   minimalist elegance, rice paper texture

   📊 变量:
   | 变量 | 默认值 | 说明 |
   |------|--------|------|
   | subject | misty mountains with pine trees | 主体 |
   | style | sumi-e brushwork | 画法 |
   | atmosphere | ethereal morning fog | 意境 |

   满意吗？可以修改任何部分。
   ```
4. Iterate until user approves

### Phase 3: Sample Generation

1. Generate 2-3 images using the drafted template with default values
2. Use different models if possible (Pro + Flash) to test compatibility
3. Present results, let user pick best samples
4. Save chosen samples to `samples/` directory
5. Record generation metadata (model, prompt, aspect) for each sample

### Phase 4: Assembly & Output

1. Ask for template metadata:
   - `id` (suggest based on title, user confirms)
   - `title` / `title_en`
   - `tags` (suggest bilingual tags based on content)
2. Assemble complete `template.md` with frontmatter + all sections
3. Validate: check required fields, variable syntax consistency, samples metadata
4. Write to output directory (default: current working directory `<id>/`)
5. Provide publishing instructions:
   ```
   ✅ 模板已创建: ink-landscape/
   ├── template.md
   └── samples/
       ├── sample-01.jpg (Pro)
       └── sample-02.jpg (Flash)

   下一步:
   1. 检查并微调 template.md
   2. 创建 GitHub 仓库并推送
   3. 其他用户安装: npx bananahub add <username>/<repo>
   4. 提交到 BananaHub: https://bananahub.github.io/submit
   ```

### Template Validation Rules

| Check | Rule | On Fail |
|-------|------|---------|
| ID format | lowercase, hyphens, 3-50 chars | Auto-fix or ask |
| Title | Non-empty Chinese title + English title | Ask |
| Profile | Must be valid profile name | Ask to choose |
| Body length | Total body < 100 lines | Trim tips or simplify prompt |
| Prompt length | Prompt Template < 80 words | Shorten; Gemini degrades with long prompts |
| Variable count | 3-6 variables with snake_case names | Merge or split variables |
| Variable defaults | Every `{{var\|default}}` has a complete-sentence default | Fill in defaults |
| Variables table | Each `{{var}}` in prompt has matching table entry | Auto-generate |
| No quality tags | No "8K", "ultra-detailed", "masterpiece", "best quality" | Remove; these are SD/MJ artifacts |
| Narrative structure | Prompt uses sentences, not comma-separated keywords | Rewrite as natural language |
| Samples | ≥ 1 sample image exists | Generate if missing |
| Sample metadata | Each sample has `model` and `prompt` in frontmatter | Auto-fill from generation |
| Tags | ≥ 3 tags, mix of Chinese + English | Suggest bilingual tags |
| Tips | Each tip is specific and testable (no vague advice) | Rewrite with concrete guidance |
