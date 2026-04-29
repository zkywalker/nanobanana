# BananaHub 规划文档

[English version](./BANANAHUB.md)

> 这份文档写给人读。给 agent 看的参考材料在 `references/template-system.md` 和 `references/template-format-spec.md`。

**版本**：0.1.0 | **状态**：进行中 | **日期**：2026-03-24

---

## 它是什么

BananaHub 是这套产品的统称。拆开来看有四块：

- **Skill runtime**：`/bananahub` 的入口，管优化、生成、改图和迭代
- **Optimization engine**：抽约束、做保守增强、需要时追问、按 profile 给引导
- **Template system**：把能复用的 prompt 或工作流封成带元数据和样例的模块，能被自动匹配
- **Distribution loop**：画廊、安装 CLI、机读目录，以及远程模板的安装量和内置模板的使用量

换句话说，BananaHub 不是一坨大 prompt，而是让可复用的 prompt 结构以"能装"的形式流通；runtime 不必什么都塞进去。

---

## 整体结构

```text
┌─────────────────────────────────────────────────────────┐
│                    BananaHub 生态                         │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Template │  │ CLI Tool │  │  Skill   │  │  Hub    │ │
│  │  Format  │  │(bananahub│  │ Runtime  │  │  Site   │ │
│  │          │  │   CLI)   │  │          │  │         │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │              │             │              │      │
│       └──────────────┴─────────────┴──────────────┘      │
│                          │                                │
│                    GitHub Repos                           │
│                    （去中心化存储）                        │
└─────────────────────────────────────────────────────────┘
```

几条设计上守着的线：

- 模板放在作者自己的 GitHub 仓库里，不做中心化托管
- 元数据全写在 `template.md` 的 frontmatter 里，模板本身就是文档
- 自动推荐匹配的模板，但不抢用户的选择
- `npx bananahub add user/repo` 就能用，不配置
- 提供 creator skill 帮用户写模板
- 发现在画廊，激活在工作流

---

## CLI：`bananahub`

**包名**：npm 上的 `bananahub` | **运行时**：Node.js（ESM） | **源码**：`/home/coder/project/nano-banana-hub/bananahub/`

### 命令

```bash
# 安装
npx bananahub add <user/repo>                    # 单模板仓库
npx bananahub add <user/repo> --template <name>  # 从多模板仓库里挑一个
npx bananahub add <user/repo> --all              # 多模板仓库里全装

# 管理
npx bananahub remove <template-id>
npx bananahub list
npx bananahub update [template-id]
npx bananahub info <template-id>

# 发现
npx bananahub search <keyword>
npx bananahub trending

# 工具
npx bananahub init                               # 新建模板仓库脚手架
npx bananahub validate [path]                    # 校验 template.md
npx bananahub registry rebuild                   # 重建本地 .registry.json
```

### `add` 做了什么

1. 拉仓库信息（GitHub API）
2. 看类型：根目录有 `template.md` 就是单模板，有 `bananahub.json` 就是多模板
3. 下载 tarball，解压到临时目录
4. 解析 frontmatter，检查必填字段，校验 samples
5. 装到 `~/.config/bananahub/templates/<id>/`
6. 写一份 `.source.json` 记录来源
7. 重建 `.registry.json`
8. fire-and-forget 上报一次安装事件

### `init` 生成的结构

```text
my-template/
├── template.md     # 预填好的 frontmatter 和占位区块
├── samples/
│   └── .gitkeep
└── README.md
```

### 安装量统计

CLI 每次 `add` 成功都会往 Hub 发一条：

```text
POST https://worker.bananahub.ai/api/installs
{ "repo": "user/repo", "template_id": "info-diagram", "cli_version": "0.1.0" }
```

后端是 Cloudflare Worker + KV（免费额度够用：100K reads/day、1K writes/day）。
不存用户身份，不记 IP，只留 `repo + template_id + timestamp`。

Hub 侧读数据：

```text
GET /api/stats?repo=user/repo → { "total_installs": 42, "weekly_installs": 7 }
GET /api/trending → [{ "repo": "...", "installs_7d": 15 }, ...]
```

### 内置模板的使用遥测

当某个模板被选中、或成功出了图，skill 会尽力上报一次匿名事件：

```text
POST https://worker.bananahub.ai/api/usage
{ "repo": "bananahub-ai/bananahub-skill", "template_id": "background-replace-edit", "event": "generate_success", "anonymous_id": "..." }
```

事件类型只有三种：

- `selected`：模板被选中
- `generate_success`：模板驱动的生图成功
- `edit_success`：模板驱动的改图成功

Hub 侧读：

```text
GET /api/usage-stats?repo=bananahub-ai/bananahub-skill&template_id=background-replace-edit
```

---

## Hub 站点：`bananahub.ai`

站点要同时服务三类访客：

- **人**：先看样例图决定要不要，再看标题、标签、装机量确认
- **Agent**：直接读 `catalog.json`、`llms.txt` 这类稳定文件，而不是去抓 HTML
- **作者**：发布自描述的仓库，哪天不想待在这儿也能带走

### 结构

```text
静态站点（GitHub Pages）
├── index.html                # 首页：搜索、浏览、热门
├── template/{id}.html        # 模板详情页（构建时生成）
├── assets/
│   ├── css/
│   └── js/
│       ├── app.js            # 前端渲染
│       └── api.js            # Hub API 客户端
└── data/
    └── catalog.json          # 目录聚合结果（GitHub Action 产出）
```

### 数据怎么流转

1. 作者通过 PR 把自己的仓库 URL 加到 `catalog-source.json`
2. 每天跑一次的 GitHub Action 去各仓库抓 `template.md` 的 frontmatter 和样例 URL，拼成 `catalog.json`
3. 站点读 `catalog.json`，图片直接指向 `raw.githubusercontent.com`
4. 装机量从 Cloudflare Worker API 拿

### `catalog-source.json`

```json
{
  "repos": [
    "bananahub-ai/bananahub-skill",
    "bananahub-ai/templates",
    "user-a/bananahub-infographics",
    "user-b/bananahub-templates"
  ]
}
```

### `catalog.json`（构建产物）

```json
{
  "generated_at": "2026-03-24T00:00:00Z",
  "templates": [
    {
      "id": "info-diagram",
      "title": "信息图一页卡",
      "title_en": "Practical Infographic One-Pager",
      "description": "把步骤、对比或框架压缩成一张清晰信息图",
      "author": "user-a",
      "repo": "user-a/bananahub-infographics",
      "profile": "diagram",
      "tags": ["信息图", "流程图", "one-pager"],
      "difficulty": "beginner",
      "models": [{ "name": "gemini-3-pro-image-preview", "quality": "best" }],
      "samples": [{
        "url": "https://raw.githubusercontent.com/user-a/bananahub-infographics/main/samples/sample-01.jpg",
        "model": "gemini-3-pro-image-preview",
        "prompt": "Cyberpunk city street at night..."
      }],
      "install_count": 42,
      "version": "1.0.0"
    }
  ]
}
```

### 站点上能做什么

| 功能 | 说明 |
|---|---|
| Browse | 模板卡片网格：样例图、标题、标签、装机量 |
| Search | 前端按标题、标签、描述搜（中英都能匹配） |
| Filter | 按 profile、难度、模型支持情况过滤 |
| Sort | 按装机量、时间、名称排 |
| Detail page | 完整模板信息：样例、模型和 prompt、变量、安装命令 |
| Install button | 一键复制 `npx bananahub add user/repo` |
| Submit | 跳到 catalog 仓库发 PR |
| Leaderboard | 总榜和周榜 |

### 模板卡片

```text
┌─────────────────────────────┐
│  [sample-01.jpg preview]    │
│                             │
│  信息图一页卡            │
│  Practical Infographic One-Pager  │
│                             │
│  📊 diagram  ⭐ beginner      │
│  🏷️ 信息图 流程图 one-pager      │
│                             │
│  by user-a  📥 42 installs  │
│  Models: Pro ✅ Flash ✅     │
│                             │
│  [Copy Install Command]     │
└─────────────────────────────┘
```

---

## 路线图

### Phase 1：地基 ✅

- [x] `template.md` 格式定稿
- [x] 5 个内置示例模板，按最佳实践校验过
- [x] `SKILL.md` 里接好 `templates` / `use` / `create-template` 路由
- [x] Phase 2.1 加入自动匹配
- [x] creator skill 流程
- [x] 内置 + 已安装双路径搜索
- [x] `.registry.json` 自动生成
- [x] agent 文档按需加载的三层结构
- [ ] 给内置模板补真实样例图

### Phase 2：CLI ✅

- [x] 初始化 npm 包
- [x] `add`：GitHub tarball → 校验 → 安装 → 上报
- [x] `remove`、`list`、`update`、`info`
- [x] `init` 脚手架
- [x] `validate`
- [x] `search` / `trending`（先对接占位 API）
- [ ] 发到 npm

### Phase 3：Hub 后端

- [ ] Cloudflare Worker：装机量 API
- [ ] KV：按 repo / template 存装机量
- [ ] 端点：`POST /installs`、`GET /stats`、`GET /trending`
- [ ] 限流和基本校验

### Phase 4：Hub 站点

- [ ] 静态站点脚手架（HTML/CSS/JS，部署到 GitHub Pages）
- [ ] `catalog-source.json` 的提交流程
- [ ] GitHub Action：从源仓库聚合 `catalog.json`
- [ ] 模板卡片网格 + 搜索 / 筛选
- [ ] 模板详情页
- [ ] 榜单 / 热门
- [ ] 移动端适配

### Phase 5：打磨

- [ ] 模板版本管理和更新提醒
- [ ] 合集 / curated lists
- [ ] 用户主页（链到 GitHub）
- [ ] 评论 / 评分（大概基于 GitHub Discussions）
- [ ] 站点双语

---

## 相关仓库

| 仓库 | 用途 | 状态 |
|---|---|---|
| `bananahub`（npm） | CLI | ✅ 已构建，路径：`/home/coder/project/nano-banana-hub/bananahub/` |
| `bananahub-ai.github.io` | Hub 静态站点 | ✅ 已上线：`https://bananahub.ai` |
| `bananahub-api` | 装机量 Cloudflare Worker | ✅ 已上线 |
| `bananahub-skill` | 官方 skill 和内置模板 | ✅ 已上线 |
