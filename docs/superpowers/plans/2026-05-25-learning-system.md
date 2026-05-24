# 异步学习系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建一个从 GitHub Issues 输入需求 → 定时生成教案 → MkDocs 部署 → 飞书通知的完整异步学习系统。

**Architecture:** GitHub Actions cron job 扫描带 `待生成` label 的 Issues，调用 Claude API 生成教案 markdown，commit 到 chapters/，触发 MkDocs Material 构建部署到 GitHub Pages，最后通过飞书 CLI/webhook 推送通知。

**Tech Stack:** GitHub Actions, Claude API (Anthropic SDK), MkDocs Material, GitHub Pages, 飞书 CLI/webhook

---

## File Structure

```
engineering-learning/
├── mkdocs.yml                              # MkDocs 配置
├── docs/                                   # MkDocs 源文件目录
│   ├── index.md                            # 首页/进度索引
│   └── chapters/                           # 教案目录（MkDocs 从这里读）
│       └── (generated .md files)
├── .github/
│   └── workflows/
│       └── learning-system.yml             # 统一 workflow：生成 + 部署 + 通知
├── scripts/
│   ├── generate-chapters.py                # 扫描 Issues + 调用 Claude API 生成教案
│   └── notify-feishu.py                    # 飞书推送通知
├── prompts/
│   └── chapter-system-prompt.md            # 教案生成的 system prompt 模板
└── requirements.txt                        # Python 依赖（anthropic, requests 等）
```

**设计决策：**
- MkDocs 的 `docs/` 目录作为站点源，教案放在 `docs/chapters/` 下（MkDocs 约定）
- 用一个统一的 workflow 文件而不是三个分开的（生成 → 部署 → 通知是线性依赖关系）
- 生成脚本和通知脚本分开（职责分离），但由同一个 workflow 串联

---

### Task 1: MkDocs Material 基础站点搭建

**Files:**
- Create: `mkdocs.yml`
- Create: `docs/index.md`
- Create: `docs/chapters/.gitkeep`
- Create: `requirements.txt`

- [ ] **Step 1: 创建 MkDocs 配置文件**

```yaml
# mkdocs.yml
site_name: 工程知识学习
site_url: https://xzz-amu.github.io/engineering-learning/
site_description: 为产品设计师定制的工程基础教材

theme:
  name: material
  language: zh
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: 切换到深色模式
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: 切换到浅色模式
  features:
    - navigation.instant
    - navigation.tabs
    - navigation.top
    - toc.follow
    - search.suggest

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - toc:
      permalink: true

nav:
  - 首页: index.md
  - 教案:
    - chapters/p0-api-design.md
    - chapters/p0-database-basics.md
    - chapters/p0-network-protocols.md
    - chapters/p0-auth-and-permissions.md
```

- [ ] **Step 2: 创建首页**

```markdown
# 工程知识学习

为产品设计师定制的工程基础教材。目标不是学会写代码，而是达到能跟研发平等对话的水平。

## 学习进度

| 章节 | 状态 |
|------|------|
| API 设计 | 待学习 |
| 数据库基础 | 待学习 |
| 网络协议 | 待学习 |
| 认证与权限 | 待学习 |

## 如何使用

1. 在 [GitHub Issues](https://github.com/XZZ-amu/engineering-learning/issues) 提出想学的知识点
2. 系统每天晚上自动生成教案
3. 第二天收到飞书通知，点击链接阅读
4. 读完有问题回来跟 Claude 聊
```

- [ ] **Step 3: 创建 requirements.txt**

```
mkdocs-material>=9.5
anthropic>=0.30.0
requests>=2.31.0
```

- [ ] **Step 4: 创建 chapters 目录占位**

```bash
touch docs/chapters/.gitkeep
```

- [ ] **Step 5: 本地验证 MkDocs 能跑**

Run: `pip install mkdocs-material && mkdocs serve`
Expected: 本地 http://127.0.0.1:8000 能看到站点，首页正常渲染中文

- [ ] **Step 6: Commit**

```bash
git add mkdocs.yml docs/ requirements.txt
git commit -m "feat: add MkDocs Material site scaffolding"
```

---

### Task 2: GitHub Pages 部署 Workflow

**Files:**
- Create: `.github/workflows/deploy-site.yml`

- [ ] **Step 1: 创建部署 workflow**

```yaml
# .github/workflows/deploy-site.yml
name: Deploy MkDocs to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install mkdocs-material

      - name: Build site
        run: mkdocs build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site/

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: 在 GitHub repo settings 开启 Pages（source: GitHub Actions）**

Run: `gh api repos/XZZ-amu/engineering-learning/pages -X PUT -f build_type=workflow -f source.branch=main -f source.path=/`
Expected: Pages 配置成功（如果报错 409 说明已配置，忽略）

- [ ] **Step 3: Commit 并 push 验证部署**

```bash
git add .github/workflows/deploy-site.yml
git commit -m "feat: add GitHub Pages deployment workflow"
git push
```

Expected: Actions 触发，几分钟后 https://xzz-amu.github.io/engineering-learning/ 可访问

---

### Task 3: 教案生成 System Prompt

**Files:**
- Create: `prompts/chapter-system-prompt.md`

- [ ] **Step 1: 创建 system prompt 模板**

```markdown
你是一位为产品设计师定制的工程知识教师。你的学生有以下特征：

- 产品设计师，不懂代码
- 已经在用 Claude Code 做 vibe coding（有 Mindloop 项目实践经验）
- 目标：达到开发实习生水平，能跟研发平等对话
- 学习方式偏好：先问问题摸底 → 用生活类比解释 → 用真实案例举例 → 出题验证

## 已掌握的知识（不需要重复解释）

- Git 全套操作
- 代码架构五大原则和七种模式
- 部署与运维全流程
- Spec 与开发流程

## 教材写作要求

1. 用生活类比解释每个概念，不用技术黑话
2. 用 Mindloop（一个 Electron + React 桌面端笔记应用）或真实产品的案例举例
3. 控制在 10-15 分钟阅读量（约 2000-3000 字）
4. 每个章节结构：
   - 开头：一句话说清这个知识点"是什么、解决什么问题"
   - 正文：生活类比 → 技术解释 → 真实案例
   - 末尾："考考你"环节（2-3 道选择题或简答题，附答案）
5. 如果引用代码，用最简单的伪代码或 curl 命令，不要求能运行
6. 语气：像一个耐心的学长在跟你聊天，不是教科书

## 输出格式

直接输出 markdown 格式的教案内容，不需要额外包装。
```

- [ ] **Step 2: Commit**

```bash
git add prompts/chapter-system-prompt.md
git commit -m "feat: add chapter generation system prompt"
```

---

### Task 4: 教案生成脚本

**Files:**
- Create: `scripts/generate-chapters.py`

- [ ] **Step 1: 编写生成脚本**

```python
#!/usr/bin/env python3
"""扫描 GitHub Issues 中带 '待生成' label 的 Issue，调用 Claude API 生成教案。"""

import os
import json
import subprocess
from pathlib import Path
from anthropic import Anthropic

REPO = "XZZ-amu/engineering-learning"
LABEL_PENDING = "待生成"
LABEL_DONE = "已生成"
CHAPTERS_DIR = Path("docs/chapters")
PROMPTS_DIR = Path("prompts")


def get_pending_issues():
    """获取所有带 '待生成' label 的 Issues。"""
    result = subprocess.run(
        ["gh", "issue", "list", "--repo", REPO, "--label", LABEL_PENDING,
         "--json", "number,title,body", "--limit", "50"],
        capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def generate_chapter(issue: dict) -> str:
    """调用 Claude API 生成教案内容。"""
    client = Anthropic()
    system_prompt = (PROMPTS_DIR / "chapter-system-prompt.md").read_text()

    user_message = f"""请为以下知识点生成一篇教案：

## 知识点标题
{issue['title']}

## 学习目标和覆盖内容
{issue['body']}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


def save_chapter(issue: dict, content: str) -> Path:
    """将生成的教案保存到文件。"""
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    # 从 Issue title 中提取文件名，如 "P0-1: API 设计" -> "p0-api-design.md"
    title = issue["title"]
    # 去掉 "P0-1: " 前缀，取知识点名称
    if ":" in title:
        name_part = title.split(":", 1)[1].strip()
    else:
        name_part = title
    # 简单的中文 -> 拼音/英文映射，这里用 Issue number 作为备选
    filename = f"chapter-{issue['number']:02d}.md"
    filepath = CHAPTERS_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath


def update_issue_label(issue_number: int):
    """将 Issue 的 label 从 '待生成' 改为 '已生成'。"""
    subprocess.run(
        ["gh", "issue", "edit", str(issue_number), "--repo", REPO,
         "--remove-label", LABEL_PENDING, "--add-label", LABEL_DONE],
        check=True
    )


def comment_on_issue(issue_number: int, filepath: Path):
    """在 Issue 上 comment 通知教案已生成。"""
    site_url = f"https://xzz-amu.github.io/engineering-learning/chapters/{filepath.stem}/"
    comment = f"✅ 教案已生成！\n\n📖 [点击阅读]({site_url})"
    subprocess.run(
        ["gh", "issue", "comment", str(issue_number), "--repo", REPO, "--body", comment],
        check=True
    )


def main():
    issues = get_pending_issues()
    if not issues:
        print("没有待生成的 Issue")
        return

    generated = []
    for issue in issues:
        print(f"正在生成: {issue['title']}...")
        content = generate_chapter(issue)
        filepath = save_chapter(issue, content)
        update_issue_label(issue["number"])
        comment_on_issue(issue["number"], filepath)
        generated.append({"title": issue["title"], "path": str(filepath)})
        print(f"  完成: {filepath}")

    # 输出生成结果供后续步骤使用
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"generated={json.dumps(generated, ensure_ascii=False)}\n")
            f.write(f"count={len(generated)}\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 验证脚本语法正确**

Run: `python -c "import ast; ast.parse(open('scripts/generate-chapters.py').read()); print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add scripts/generate-chapters.py
git commit -m "feat: add chapter generation script (Claude API + GitHub Issues)"
```

---

### Task 5: 飞书通知脚本

**Files:**
- Create: `scripts/notify-feishu.py`

- [ ] **Step 1: 调研飞书 CLI 或 webhook 方案**

Run: `gh search repos "feishu cli" --sort stars --limit 5 --json fullName,description,stargazersCount`

根据调研结果决定：用飞书 CLI 还是直接用飞书 webhook（群机器人）。

飞书 webhook 方案更简单可靠（不依赖第三方 CLI 工具）：创建一个飞书群 → 添加自定义机器人 → 获得 webhook URL → curl 发消息。

- [ ] **Step 2: 编写通知脚本（webhook 方案）**

```python
#!/usr/bin/env python3
"""通过飞书 webhook 推送教案生成通知。"""

import os
import sys
import json
import requests

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL")
SITE_BASE_URL = "https://xzz-amu.github.io/engineering-learning"


def send_notification(generated_chapters: list):
    """发送飞书通知。"""
    if not FEISHU_WEBHOOK_URL:
        print("警告: FEISHU_WEBHOOK_URL 未设置，跳过通知")
        return

    if not generated_chapters:
        return

    # 构建消息内容
    chapter_lines = []
    for ch in generated_chapters:
        title = ch["title"]
        path = ch["path"]
        # 从文件路径推断 URL
        stem = path.replace("docs/chapters/", "").replace(".md", "")
        url = f"{SITE_BASE_URL}/chapters/{stem}/"
        chapter_lines.append(f"📖 [{title}]({url})")

    content = f"📚 今日教案已生成（共 {len(generated_chapters)} 篇）\n\n" + "\n".join(chapter_lines)

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "📚 新教案已就绪"},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "打开学习网站"},
                            "url": SITE_BASE_URL,
                            "type": "primary"
                        }
                    ]
                }
            ]
        }
    }

    resp = requests.post(FEISHU_WEBHOOK_URL, json=payload)
    if resp.status_code == 200:
        print("飞书通知发送成功")
    else:
        print(f"飞书通知发送失败: {resp.status_code} {resp.text}")


def main():
    # 从环境变量或命令行参数读取生成结果
    generated_json = os.environ.get("GENERATED_CHAPTERS", "[]")
    generated = json.loads(generated_json)
    send_notification(generated)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Commit**

```bash
git add scripts/notify-feishu.py
git commit -m "feat: add Feishu webhook notification script"
```

---

### Task 6: 统一生成 + 部署 + 通知 Workflow

**Files:**
- Create: `.github/workflows/generate-and-notify.yml`

- [ ] **Step 1: 创建定时生成 workflow**

```yaml
# .github/workflows/generate-and-notify.yml
name: Generate Chapters & Notify

on:
  schedule:
    - cron: '0 14 * * *'  # UTC 14:00 = 北京时间 22:00
  workflow_dispatch:  # 手动触发（调试用）

permissions:
  contents: write
  issues: write

jobs:
  generate:
    runs-on: ubuntu-latest
    outputs:
      generated: ${{ steps.gen.outputs.generated }}
      count: ${{ steps.gen.outputs.count }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install anthropic requests

      - name: Generate chapters
        id: gen
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python scripts/generate-chapters.py

      - name: Commit generated chapters
        if: steps.gen.outputs.count != '0'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/chapters/
          git commit -m "docs: auto-generate chapters [skip ci]" || echo "No changes to commit"
          git push

  notify:
    runs-on: ubuntu-latest
    needs: generate
    if: needs.generate.outputs.count != '0'
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install requests

      - name: Send Feishu notification
        env:
          FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
          GENERATED_CHAPTERS: ${{ needs.generate.outputs.generated }}
        run: python scripts/notify-feishu.py
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/generate-and-notify.yml
git commit -m "feat: add scheduled chapter generation workflow (daily 22:00 CST)"
```

---

### Task 7: Issue Labels 和初始化设置

**Files:**
- 无新文件，操作 GitHub API

- [ ] **Step 1: 创建所需的 Labels**

```bash
gh label create "待生成" --color "FEF2C0" --description "等待定时任务生成教案" --repo XZZ-amu/engineering-learning
gh label create "已生成" --color "BFD4F2" --description "教案已生成，等待阅读" --repo XZZ-amu/engineering-learning
gh label create "学习中" --color "D4C5F9" --description "正在学习中" --repo XZZ-amu/engineering-learning
gh label create "已掌握" --color "C2E0C6" --description "已掌握，可关闭" --repo XZZ-amu/engineering-learning
```

- [ ] **Step 2: 给现有 4 个 Issue 加上 `待生成` label**

```bash
gh issue edit 1 --add-label "待生成" --repo XZZ-amu/engineering-learning
gh issue edit 2 --add-label "待生成" --repo XZZ-amu/engineering-learning
gh issue edit 3 --add-label "待生成" --repo XZZ-amu/engineering-learning
gh issue edit 4 --add-label "待生成" --repo XZZ-amu/engineering-learning
```

- [ ] **Step 3: 验证 labels 已创建且 Issues 已打标**

Run: `gh issue list --label "待生成" --repo XZZ-amu/engineering-learning`
Expected: 显示 4 个 Issue

- [ ] **Step 4: Commit（无文件变更，仅验证）**

无需 commit，此步骤操作的是 GitHub API。

---

### Task 8: MkDocs nav 自动更新

**Files:**
- Modify: `scripts/generate-chapters.py`（添加更新 mkdocs.yml nav 的逻辑）

- [ ] **Step 1: 在生成脚本中添加 nav 更新功能**

在 `generate-chapters.py` 的 `main()` 函数末尾，添加自动更新 `mkdocs.yml` 中 nav 配置的逻辑：

```python
def update_mkdocs_nav():
    """扫描 docs/chapters/ 目录，自动更新 mkdocs.yml 的 nav 配置。"""
    import yaml

    chapters = sorted(CHAPTERS_DIR.glob("*.md"))
    if not chapters:
        return

    mkdocs_path = Path("mkdocs.yml")
    with open(mkdocs_path) as f:
        config = yaml.safe_load(f)

    # 构建 nav 条目
    chapter_nav = []
    for ch in chapters:
        if ch.name == ".gitkeep":
            continue
        # 读取文件第一行作为标题
        first_line = ch.read_text(encoding="utf-8").split("\n")[0]
        title = first_line.lstrip("# ").strip() if first_line.startswith("#") else ch.stem
        chapter_nav.append({title: f"chapters/{ch.name}"})

    # 更新 nav
    config["nav"] = [
        {"首页": "index.md"},
        {"教案": chapter_nav}
    ]

    with open(mkdocs_path, "w") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


# 在 main() 末尾调用
# update_mkdocs_nav()
```

- [ ] **Step 2: 在 requirements.txt 中添加 PyYAML**

将 `requirements.txt` 更新为：

```
mkdocs-material>=9.5
anthropic>=0.30.0
requests>=2.31.0
pyyaml>=6.0
```

- [ ] **Step 3: 更新 workflow 中的 git add 范围**

在 `.github/workflows/generate-and-notify.yml` 的 commit 步骤中，将 `git add docs/chapters/` 改为 `git add docs/chapters/ mkdocs.yml`。

- [ ] **Step 4: Commit**

```bash
git add scripts/generate-chapters.py requirements.txt .github/workflows/generate-and-notify.yml
git commit -m "feat: auto-update mkdocs nav when chapters are generated"
```

---

### Task 9: 端到端验证

**Files:**
- 无新文件

- [ ] **Step 1: 设置 repo secrets**

需要用户手动操作（或通过 gh CLI）：

```bash
gh secret set ANTHROPIC_API_KEY --repo XZZ-amu/engineering-learning
# 输入 API key

gh secret set FEISHU_WEBHOOK_URL --repo XZZ-amu/engineering-learning
# 输入飞书 webhook URL（需要先在飞书创建群机器人）
```

注意：FEISHU_WEBHOOK_URL 需要用户先在飞书中创建一个群 → 添加自定义机器人 → 获取 webhook URL。

- [ ] **Step 2: 手动触发 workflow 验证全流程**

```bash
gh workflow run generate-and-notify.yml --repo XZZ-amu/engineering-learning
```

- [ ] **Step 3: 等待执行完成并验证**

Run: `gh run list --workflow=generate-and-notify.yml --repo XZZ-amu/engineering-learning --limit 1`

验证：
1. workflow 成功完成（status: completed, conclusion: success）
2. `docs/chapters/` 目录下生成了 4 个 markdown 文件
3. 4 个 Issue 的 label 变为 `已生成`
4. 每个 Issue 下有 comment 带阅读链接
5. GitHub Pages 站点可访问且显示教案内容
6. 飞书收到通知消息

- [ ] **Step 4: 如果失败，检查 workflow 日志排查问题**

```bash
gh run view <run-id> --log --repo XZZ-amu/engineering-learning
```

---

## 执行顺序和依赖关系

```
Task 1 (MkDocs 站点) ──┐
Task 3 (System Prompt) ─┼─→ Task 4 (生成脚本) ─→ Task 8 (Nav 更新)
                        │
Task 2 (Pages 部署) ────┘
                                                         ↓
Task 5 (飞书通知) ─→ Task 6 (统一 Workflow) ─→ Task 7 (Labels) ─→ Task 9 (验证)
```

可并行的任务：
- Task 1 + Task 2 + Task 3 可以并行
- Task 4 + Task 5 可以并行（互不依赖）

---

## Secrets 清单（需要用户配置）

| Secret 名称 | 用途 | 获取方式 |
|-------------|------|----------|
| `ANTHROPIC_API_KEY` | 调用 Claude API 生成教案 | Anthropic Console |
| `FEISHU_WEBHOOK_URL` | 飞书消息推送 | 飞书群设置 → 自定义机器人 → webhook URL |

---

## 验收标准（对应 Spec）

1. ✅ 带 `待生成` label 的 Issue → 定时任务运行后 chapters/ 里出现对应教案文件
2. ✅ GitHub Pages 上能访问排版好的教材网站，手机/PC 均可正常阅读
3. ✅ 飞书收到通知消息，包含教案标题 + 阅读链接
4. ✅ 现有 4 个 P0 Issue 作为首批测试素材，定时任务跑完后应全部生成
