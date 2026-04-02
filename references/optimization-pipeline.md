# Prompt Optimization Pipeline

When the user provides a Chinese description, process it through this pipeline (executed by you, not the script).

## Phase 0: Constraint Extraction

Before optimizing wording, extract the request's hard constraints into a simple internal checklist.

Capture these when present:
- `exact_text`: text that must appear verbatim in the image
- `must_keep`: elements the user explicitly wants preserved
- `must_avoid`: styles, objects, colors, or treatments the user does not want
- `target_use`: poster, logo, avatar, wallpaper, e-commerce listing, slide diagram, etc.
- `target_platform`: 淘宝、小红书、微信贴纸、PPT、社交媒体封面等
- `style_lock`: explicit style words the skill must not override
- `open_variables`: still-ambiguous decisions that could materially change the result

For edit requests, also extract `invariants`:
- subject identity
- composition / crop
- background
- text / logo
- palette / material / outfit
- anything the user said should stay the same

When the request is a follow-up on an already accepted result, also extract:
- `approved_baseline`: the exact accepted file or prompt state that becomes the only source of truth
- `locked_invariants`: the exact silhouette, text, count, proportion, border, spacing, or layout properties that must remain unchanged
- `allowed_delta`: the single change this round is allowed to make
- `derivation_mode`: whether this is still a creative model task or a deterministic asset-derivation task

If a hard constraint is critical but unclear, ask before generating in default mode. If the user did not provide a constraint, do not invent one.

## Phase 1: Base Optimization (always on, silent)

Runs in all modes except `--raw`. Always perform these steps:

### 1. Format Correction
Refer to `references/prompt-guide.md` error detection rules:
- Keyword list pattern → rewrite as natural language
- SD/MJ weight syntax `(word:1.5)` → remove
- Negative phrasing → restate positively
- Buried subject → move to front
- Quality tag spam → delete

### 2. Smart Translation
Translate descriptions into natural English, distinguishing two types of text:

**Language policy for the final prompt**:
- The final prompt should be written in natural English by default
- Preserve original-language text only for:
  - in-image text that must appear verbatim
  - proper nouns / brand names / titles that should not be translated
  - user-specified labels that must stay in Chinese or another source language
- Do not leave descriptive clauses, enhancement notes, or structural instructions in Chinese unless the user explicitly requires that

**Descriptive text** (translate): sentences describing the scene
- `穿红裙子的女孩` → "a girl wearing a red dress"

**In-image text** (preserve original language): text the user wants displayed in the image
- Recognition signals: quoted content, text following "写着/印着/显示/标注/刻着"
- `写着"生日快乐"的蛋糕` → `a cake with the text "生日快乐"`
- `T恤上印着"HELLO"` → `a T-shirt with "HELLO" printed on it` (English in-image text also preserved as-is)
- Text longer than 25 characters → warn user, suggest shortening

### 3. Structuring
- Ensure the image subject is at the beginning of the prompt
- Add trigger prefix: "Create an image of" or another suitable action phrase

### 4. Conservative Enhancement Guardrail
- Preserve user intent over "prompt beautification"
- Only add details that are:
  - explicitly requested
  - strongly implied by the task type
  - necessary for readability or technical correctness
- Do **not** casually add high-impact visual decisions such as:
  - background material or setting
  - palette / accent colors
  - lighting mood / time of day
  - lens, depth of field, camera angle
  - paper / whiteboard / notebook texture
  - extra props, scenery, or invented character actions
- If an addition changes the look more than it clarifies the request, leave it out
- In default mode, when a high-impact addition would noticeably shape the final look, ask/confirm instead of assuming
- In direct mode, stay conservative rather than becoming more speculative

### 5. Clarification Triggers
- Ask a concise follow-up in default mode when there are multiple plausible directions and the choice would materially change the result
- Typical cases:
  - missing poster / logo / invitation text or unstable copy
  - product/platform requests where background, ratio, or composition depends on the target platform
  - diagram / sketchnote requests where layout choice changes reading order
  - photo / 3D / concept-art requests where lens, render finish, or mood would dominate the image
- If the user does not answer, omit the high-impact detail rather than guessing

### 6. Baseline-Lock Routing
- When the user is iterating on an accepted image, treat that accepted file as the only baseline until a newer version is explicitly approved
- Restate locked invariants explicitly in the final prompt instead of leaving them implicit in a reference image
- Name the one allowed delta for the current round; if there are multiple requested changes, split them into separate rounds when practical
- Prefer source-image editing over fresh generation once a baseline exists
- If the request is a deterministic derivative such as invert, crop, export, add safe padding, or place an approved icon beside exact final text, prefer a local deterministic transform instead of asking the model to redraw the asset

## Phase 2: Intent Recognition

Analyze user input and match the most appropriate enhancement Profile:

| Profile | Signal keywords |
|---------|----------------|
| `photo` | 照片、写实、人像、风景、风光、街拍、摄影、真实感 |
| `illustration` | 插画、漫画、动漫、卡通、手绘、像素画、水彩画、油画、同人、国风 |
| `diagram` | 图表、流程图、架构图、信息图、示意图、讲解图、总结图、教程图、知识卡片、explainer |
| `text-heavy` | Logo、海报、名片、菜单、标牌、封面、横幅、邀请函、贺卡 |
| `minimal` | 极简、留白、壁纸、纯色、简约 |
| `sticker` | 表情包、贴纸、meme、梗图、emoji、sticker |
| `3d` | 3D、渲染、建模、等距、isometric、建筑效果图、室内设计 |
| `product` | 产品图、商品、电商、淘宝、主图、白底图 |
| `concept-art` | 概念设计、原画、角色设计、游戏角色、splash art |
| `general` | No clear match to the above categories |

**Recognition logic**:
1. Scan user input for keywords → direct match
2. If multiple profiles match → apply conflict disambiguation rules from `references/prompt-guide.md`
3. No keyword hit → infer from semantic context (person + scene → photo, art style mentioned → illustration)
4. Still uncertain → fall back to `general`
5. **Principle: prefer falling back to general (less optimization) over guessing wrong and distorting intent**

### Phase 2.1: Local Template Auto-Matching (Progressive Disclosure)

After profile matching, check if any installed template closely matches the user's input:

1. **Load template index**: read `.registry.json` from both template search paths (see `references/template-system.md`)
2. **Match by tags + title**: compare user input keywords against each template's `tags` and `title`
3. **Score**: count keyword overlaps; threshold ≥ 2 tag matches to suggest
4. **Default mode** — if a match is found:
   ```
   Matching template found: cyberpunk-city (Cyberpunk City Nightscape)
   Fit: ⭐⭐⭐ (3 keyword hits)

   Choose:
   1. Use template
   2. Continue regular optimization
   ```
   If user chooses template → switch to `use <template-id>` flow.
   If user chooses regular → continue normal Phase 3.
   When the matched template has `type: prompt`, activation means assembling the prompt and generating.
   When the matched template has `type: workflow`, activation means loading the workflow context and guiding the user step-by-step.
5. **Direct mode** — auto-use best match if score ≥ 3, otherwise regular flow
6. **Raw mode** — skip template matching entirely

### Phase 2.2: BananaHub Remote Discovery (On Demand)

Use remote discovery only when at least one of these is true:

- the user explicitly asks Nano Banana to find or recommend a template
- local matches are weak or missing
- the task looks highly repeatable and likely has a reusable workflow on BananaHub

Flow:

1. Read `references/hub-discovery.md`
2. Prefer curated BananaHub results by default; expand to merged/community results only when needed
3. Rank by relevance first, then `pinned` / `featured` / curated / official
4. Show a shortlist instead of a full dump
5. Ask once whether to install the best match, inspect another candidate, or continue regular optimization
6. If the user installs a candidate, immediately switch to the normal `use <template-id>` flow
7. Do not load the full remote template body during broad search unless a shortlist candidate needs closer inspection

**Special routing note**:
- `手绘笔记 / sketchnote / 白板风 / 手账风` is **not** a standalone Profile
- First identify the underlying task type (`diagram`, `text-heavy`, `illustration`, etc.), then treat the hand-drawn request as an overlay
- Explanations, workflows, comparisons, summaries, tutorials, project intros → usually `diagram` or `text-heavy`
- Character or scene art → usually `illustration`

## Phase 2.5: Style Overlay Detection

Before enhancement, detect optional style overlays that modify the matched Profile without replacing it.

### `hand-drawn-sketch-note` overlay

**Signal keywords**:
- 手绘笔记、手绘说明图、白板风、手账风、草图说明、sketchnote、sketch note、whiteboard sketch、hand-drawn note

**Apply rules**:
1. Read the hand-drawn sketch-note section in `references/prompt-guide.md`
2. Keep the matched functional Profile as the base (`diagram`, `text-heavy`, or `illustration`)
3. Merge only the overlay rules that fit the user's intent
4. Prefer structure-related cues over palette/background cues:
   - arrows / numbering / callout boxes
   - grouped regions and clear reading order
   - short labels instead of dense paragraphs
5. Only add white background / black marker linework / accent colors when they are explicit or strongly implied by the subtype
6. If the user only wants a hand-drawn aesthetic for a character or scene, do **not** force a note-card layout

## Phase 3: Enhancement (on-demand, lazy-loaded)

If intent recognition matched a specific Profile (not general):

1. **Read the corresponding Profile file**: `Read` `references/profiles/{profile_name}.md`
2. **Classify the subject** before enhancing (see Subject Classification below)
3. **Fill in missing dimensions per Profile rules and any detected overlay rules**: only add what the user didn't mention; never override existing expressions
4. **Decide whether to confirm based on mode**:
   - Default mode → show enhanced result, wait for user to confirm/edit/reject
   - Direct mode → use enhanced result directly

### Subject Classification

Before adding any enhancement, classify the subject into one of these categories and apply corresponding constraints:

| Subject Type | Examples | Enhancement Strategy |
|---|---|---|
| **Known IP character** | Tachikoma, Pikachu, R2-D2, Totoro, Iron Man | **Only enhance user-implied presentation cues. Do NOT add appearance descriptions** — the model already knows what these characters look like. Vague or inaccurate descriptions override the model's correct knowledge and cause distortion. |
| **Non-humanoid entity** | Robots, vehicles, animals, abstract creatures | **Avoid anthropomorphic language** — no "eyes", "smile", "face", "chibi proportions". Use form-appropriate terms: "compact design", "rounded silhouette", "soft curves", "bright color palette". |
| **Original / generic character** | "a girl", "an old man", "a warrior" | Keep enhancements conservative. Only add appearance, pose, or expression details when the user already implies them or when they are necessary to make the request coherent. |
| **Scene / object** | Landscapes, food, still life, architecture | Keep enhancements conservative. Only add environment, lighting, or material details when the scene already implies them or they are necessary for task fidelity. |

**Key principles**:
- **Ambiguous terms are worse than no terms** — if a word could be misinterpreted (e.g., "optical eyes" on a robot → model renders human eyes), do not add it. Only use unambiguous descriptors.
- **"Cute" ≠ anthropomorphic** — for non-humanoid subjects, express cuteness through: rounded shapes, bright/pastel colors, compact proportions, soft lighting, playful composition. NOT through adding faces, expressions, or chibi features.
- **Less is more for known characters** — the model's built-in knowledge of famous characters is usually more accurate than our text descriptions. Trust it.
- **A reference is not a lock by itself** — if exact consistency matters, write the keep-unchanged constraints explicitly instead of assuming the model will infer them

### Default Mode Confirmation Format

```
📋 识别意图: [Profile name]
📝 基础优化: [base-optimized prompt]
📌 硬约束: [exact text / must keep / avoid / platform, if any]
❓ 待确认: [only when needed]
✨ 增强建议: [fully enhanced prompt]
   安全补充: +[structural / low-risk additions]
   高影响补充: +[style / background / lighting / palette / lens choices, if any]

选择: 确认增强 / 使用基础版本 / 修改
```

If `general` was matched: skip enhancement confirmation, generate directly with the base-optimized result.

## Iteration Discipline

- Change one major variable at a time
- Treat accepted outputs as approved baselines, not just loose inspiration
- Use exact keep-unchanged language in follow-up edit prompts when silhouette, copy, spacing, or layout must stay fixed
- Route deterministic derivatives away from the model when the desired result is a non-creative transform
