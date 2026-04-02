# BananaHub — 项目规划文档

[English version](./BANANAHUB.md)

> 这是一份给人读的 BananaHub 模板生态规划文档。
> 如果是给 agent 看的参考，请看 `references/template-system.md`、`references/template-system.zh-CN.md`、`references/template-format-spec.md` 和 `references/template-format-spec.zh-CN.md`。

**版本**：0.1.0 | **状态**：进行中 | **日期**：2026-03-24

---

## 产品定位

BananaHub 是这套产品的统一品牌。落到实现上，目前可以拆成四层：

- **BananaHub Skill runtime**：agent-native 的 `/bananahub` 交互入口，负责优化、生成、编辑和迭代
- **Optimization engine**：负责约束提取、保守增强、渐进式澄清和按 profile 引导
- **Template system**：把可复用的 prompt 或 workflow 能力沉淀成带元数据、样例和自动匹配能力的模块
- **BananaHub distribution loop**：负责可搜索的画廊、安装 CLI、机器可读目录和安装 / 热度数据

所以 BananaHub 不是一个巨大的 prompt 文本堆，而是让可复用 prompt 结构以“可安装模块”的方式流通，同时避免运行时膨胀成一个大而全的单体。

---

## 架构概览

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

**设计原则**：

- 去中心化：模板存放在作者自己的 GitHub 仓库里
- 自描述：模板元数据全部写在 `template.md` frontmatter 里
- 渐进式展开：自动推荐匹配模板，但不强行替用户切模板
- 零配置：`npx bananahub add user/repo` 后即可使用
- AI 原生：提供 creator skill，让 AI 协助用户创建模板
- 可搜索 + 可安装：发现发生在画廊里，激活发生在工作流里

---

## CLI 工具：`bananahub`

**包名**：npm 上的 `bananahub` | **语言**：Node.js（ESM） | **源码**：`/home/coder/project/nano-banana-hub/bananahub/`

### 命令

```bash
# 安装
npx bananahub add <user/repo>                    # 安装单模板仓库
npx bananahub add <user/repo> --template <name>  # 从多模板仓库安装指定模板
npx bananahub add <user/repo> --all              # 安装多模板仓库里的全部模板

# 管理
npx bananahub remove <template-id>               # 卸载模板
npx bananahub list                               # 列出已安装模板
npx bananahub update [template-id]               # 更新一个或全部模板
npx bananahub info <template-id>                 # 查看模板详情

# 发现
npx bananahub search <keyword>                   # 搜索 Hub 模板
npx bananahub trending                           # 查看热门模板

# 工具
npx bananahub init                               # 初始化一个新模板仓库（脚手架）
npx bananahub validate [path]                    # 校验 template.md 格式
npx bananahub registry rebuild                   # 重建本地 .registry.json
```

### `add` 流程

1. **解析仓库**：通过 GitHub API 拉取仓库信息
2. **识别类型**：根目录有 `template.md` 则为单模板；有 `bananahub.json` 则为多模板
3. **下载内容**：通过 GitHub tarball API 下载并解压到临时目录
4. **校验模板**：解析 frontmatter、检查必填字段、验证 samples
5. **安装文件**：复制到 `~/.config/bananahub/templates/<id>/`
6. **写 `.source.json`**：记录来源信息
7. **重建 registry**：重新生成 `.registry.json`
8. **上报安装**：向 Hub API 发送安装事件（fire-and-forget）

### `init` 脚手架

交互提问后生成：

```text
my-template/
├── template.md     # 预填好的 frontmatter 和占位区块
├── samples/
│   └── .gitkeep
└── README.md
```

### 安装量统计

**机制**：每次 `add` 都由 CLI 向 Hub API 发 POST：

```text
POST https://bananahub-api.workers.dev/api/installs
{ "repo": "user/repo", "template_id": "cyberpunk-city", "cli_version": "0.1.0" }
```

**后端**：Cloudflare Worker + KV（免费额度：100K reads/day，1K writes/day）
**隐私**：不记录用户身份，不记录 IP，只存 `repo + template_id + timestamp`

**Hub 读取接口**：

```text
GET /api/stats?repo=user/repo → { "total_installs": 42, "weekly_installs": 7 }
GET /api/trending → [{ "repo": "...", "installs_7d": 15 }, ...]
```

---

## Hub 站点：`bananahub.github.io`

BananaHub 的站点同时服务三类对象：

- **人类用户**：先按生成结果浏览，再用标题、标签和安装命令做确认
- **Agent**：直接读取 `catalog.json`、`llms.txt` 等稳定文件，而不是抓页面卡片
- **模板作者**：发布可自描述、可迁移的仓库，而不是把内容锁死在平台里

### 架构

```text
静态站点（GitHub Pages）
├── index.html                # 主页面：搜索、浏览、热门
├── template/{id}.html        # 模板详情页（生成）
├── assets/
│   ├── css/
│   └── js/
│       ├── app.js            # 前端渲染逻辑
│       └── api.js            # Hub API 客户端
└── data/
    └── catalog.json          # 模板目录聚合结果（由 GitHub Action 构建）
```

### 数据流

1. 模板作者通过 PR 向 `catalog-source.json` 提交仓库 URL
2. GitHub Action（每天执行）读取各仓库的 `template.md`，抽取 frontmatter 和 sample URL，构建 `catalog.json`
3. 静态站点读取 `catalog.json`，并直接使用 `raw.githubusercontent.com` 上的图片
4. 安装量数据来自 Cloudflare Worker API

### `catalog-source.json`

```json
{
  "repos": [
    "user-a/bananahub-cyberpunk",
    "user-b/bananahub-templates",
    "bananahub-ai/banana-hub-skill"
  ]
}
```

### `catalog.json`（构建产物）

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
      "repo": "user-a/bananahub-cyberpunk",
      "profile": "photo",
      "tags": ["赛博朋克", "城市", "夜景"],
      "difficulty": "beginner",
      "models": [{ "name": "gemini-3-pro-image-preview", "quality": "best" }],
      "samples": [{
        "url": "https://raw.githubusercontent.com/user-a/bananahub-cyberpunk/main/samples/sample-01.jpg",
        "model": "gemini-3-pro-image-preview",
        "prompt": "Cyberpunk city street at night..."
      }],
      "install_count": 42,
      "version": "1.0.0"
    }
  ]
}
```

### 网站功能

| 功能 | 说明 |
|---|---|
| **Browse** | 模板卡片网格：样例图、标题、标签、安装量 |
| **Search** | 按标题、标签、描述做前端搜索（中英双语） |
| **Filter** | 按 profile、难度、模型支持情况筛选 |
| **Sort** | 按安装量（热门）、时间（最新）、名称排序 |
| **Detail page** | 展示完整模板信息：样例、模型 / prompt、变量、安装命令 |
| **Install button** | 一键复制 `npx bananahub add user/repo` |
| **Submit** | 跳转到 catalog 仓库发 PR |
| **Leaderboard** | 展示总榜 / 周榜热门模板 |

### 模板卡片 UI

```text
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

## 实现路线图

### Phase 1：基础设施 ✅

- [x] 定义模板格式（`template.md` 规范）
- [x] 提供 5 个内置示例模板，并按最佳实践校验
- [x] 在 `SKILL.md` 中接入 `templates` / `use` / `create-template` 路由
- [x] 在 Phase 2.1 加入自动匹配逻辑
- [x] 实现 creator skill 流程
- [x] 支持内置模板 + 已安装模板双路径搜索
- [x] 自动生成 `.registry.json`
- [x] 搭好三层按需加载的 agent 文档结构
- [ ] 为内置模板生成真实样例图

### Phase 2：CLI 工具 ✅

- [x] 初始化 npm 包 `bananahub`
- [x] 实现 `add` 命令（GitHub tarball → 安装 → 上报）
- [x] 实现 `remove`、`list`、`update`、`info`
- [x] 实现 `init` 脚手架
- [x] 实现 `validate`
- [x] 实现 `search` / `trending`（暂时对接占位 Hub API）
- [ ] 发布到 npm

### Phase 3：Hub 后端

- [ ] Cloudflare Worker：安装量 API
- [ ] Cloudflare KV：按 repo / template 记录安装量
- [ ] API 端点：`POST /installs`、`GET /stats`、`GET /trending`
- [ ] 限流和基础校验

### Phase 4：Hub 站点

- [ ] 静态站点脚手架（HTML/CSS/JS，部署到 GitHub Pages）
- [ ] `catalog-source.json` 提交流程
- [ ] GitHub Action：从源仓库构建 `catalog.json`
- [ ] 模板卡片网格 + 搜索 / 筛选
- [ ] 模板详情页
- [ ] 排行榜 / 热门模块
- [ ] 移动端响应式

### Phase 5：打磨

- [ ] 模板版本管理和更新提醒
- [ ] 模板合集 / curated lists
- [ ] 用户主页（链接 GitHub）
- [ ] 评论 / 评分（是否基于 GitHub Discussions）
- [ ] 站点 i18n（中英双语）

---

## 后续仓库

| 仓库 | 用途 | 状态 |
|---|---|---|
| `bananahub`（npm） | CLI 工具 | ✅ 已构建，路径：`/home/coder/project/nano-banana-hub/bananahub/` |
| `bananahub-ai.github.io` | Hub 静态站点 | ✅ 已上线 |
| `bananahub-api` | 安装统计的 Cloudflare Worker | ✅ 已上线 |
| `banana-hub-skill` | 官方 skill 与内置模板集合 | ✅ 已上线 |
