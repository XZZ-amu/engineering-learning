# 异步学习系统设计 Spec

## 概述

为产品设计师定制的个人异步学习系统。用户通过 GitHub Issues 提出学习需求，系统定时自动生成教案，部署为可阅读的网站，并通过飞书推送通知。

## 用户

仅一人（项目所有者），不考虑多用户。

## 核心流程

```
用户建 Issue（"我想学 XX"）
       ↓
每天定时扫描未生成的 Issue（GitHub Actions cron）
       ↓
调用 Claude API 生成教案（markdown）
       ↓
教案 commit 到 chapters/ 目录
       ↓
MkDocs Material 构建 → 部署 GitHub Pages
       ↓
飞书推送摘要 + 阅读链接
       ↓
用户阅读 → 回来答疑 → 标记已掌握 → 关闭 Issue
```

## 各模块设计

### 1. 需求输入：GitHub Issues

- 用户创建 Issue，标题为知识点名称（如 "P0-1: API 设计"）
- Issue body 包含学习目标、覆盖内容、教材要求
- 用 label 管理状态流转：
  - `待生成`：新建的 Issue，等待定时任务处理
  - `已生成`：教案已生成，等待用户阅读
  - `学习中`：用户正在学习
  - `已掌握`：用户确认掌握，Issue 关闭

### 2. 异步生成：GitHub Actions + Claude API

- 触发方式：cron 定时任务（每天晚上，具体时间待定）
- 流程：
  1. 扫描所有带 `待生成` label 的 Issue
  2. 读取 Issue body 作为生成 prompt 的上下文
  3. 读取 CLAUDE.md 中的用户画像和教材要求作为 system prompt
  4. 调用 Claude API 生成教案 markdown
  5. 将生成的文件 commit 到 `chapters/` 目录
  6. 将 Issue label 从 `待生成` 改为 `已生成`
  7. Comment 回 Issue，附上 GitHub Pages 阅读链接

### 3. 阅读体验：MkDocs Material + GitHub Pages

- 使用 MkDocs Material 主题（开箱即用的响应式设计）
- 部署到 GitHub Pages
- 默认主题先跑通，后续再调视觉
- 要求：
  - 中文排版正常
  - 代码块有语法高亮
  - 手机端可正常阅读（响应式）
  - 有侧边栏目录导航
  - 有章节内目录（TOC）

### 4. 通知推送：飞书

- 教案生成完成后，通过飞书 CLI（GitHub 上的开源工具，执行时调研具体方案）推送消息
- 消息内容：教案标题 + 一句话摘要 + GitHub Pages 阅读链接
- 推送时机：定时任务执行完毕后统一推送

### 5. 知识沉淀

- 教案文件存放在 `chapters/` 目录，每个知识点一个 markdown 文件
- 根目录维护 `INDEX.md` 作为全局进度索引
- Issue 的 label 状态反映学习进度

## 技术选型

| 组件 | 方案 | 理由 |
|------|------|------|
| CI/CD | GitHub Actions | 仓库原生支持，零额外基础设施 |
| AI 生成 | Claude API | 教案质量最好，理解中文语境 |
| 静态站点 | MkDocs Material | YAML 配置友好、中文/移动端/代码高亮开箱即用 |
| 部署 | GitHub Pages | 免费、跟仓库绑定 |
| 通知 | 飞书 CLI | 待调研确认具体工具，GitHub 上有开源方案 |

## 文件结构（预期）

```
engineering-learning/
├── CLAUDE.md
├── INDEX.md                    # 全局进度索引
├── mkdocs.yml                  # MkDocs 配置
├── chapters/                   # 教案目录
│   ├── p0-api-design.md
│   ├── p0-database-basics.md
│   ├── p0-network-protocols.md
│   └── p0-auth-and-permissions.md
├── docs/
│   └── superpowers/specs/      # 设计文档
│       └── 2026-05-25-learning-system-design.md
└── .github/
    └── workflows/
        ├── generate-chapters.yml   # 定时生成教案
        ├── deploy-site.yml         # 构建部署 MkDocs
        └── notify-feishu.yml       # 飞书通知（可能合并到上面）
```

## 验收标准

1. 带 `待生成` label 的 Issue → 定时任务运行后 chapters/ 里出现对应教案文件
2. GitHub Pages 上能访问排版好的教材网站，手机/PC 均可正常阅读
3. 飞书收到通知消息，包含教案标题 + 阅读链接
4. 现有 4 个 P0 Issue 作为首批测试素材，定时任务跑完后应全部生成

## 已知短板

- 飞书 CLI 具体方案未调研确认，可能需要换成 webhook 方案
- Claude API 有调用成本（预估极低，每篇教案约几毛钱）
- 定时任务的具体执行时间需要确定（建议晚上 22:00 或 23:00）
- 首次需要手动设置 ANTHROPIC_API_KEY 到 repo secrets

## 不做的事情

- 不做多用户
- 不做注册登录
- 不做间隔复习/Anki
- 不做知识图谱
- 不在第一版调视觉设计
