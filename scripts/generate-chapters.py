#!/usr/bin/env python3
"""扫描 GitHub Issues 中带 '待生成' label 的 Issue，调用 Claude API 生成教案，push 并通知。"""

import json
import subprocess
from pathlib import Path
from anthropic import Anthropic

REPO = "XZZ-amu/engineering-learning"
LABEL_PENDING = "待生成"
LABEL_DONE = "已生成"
PROJECT_DIR = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = PROJECT_DIR / "docs" / "chapters"
PROMPTS_DIR = PROJECT_DIR / "prompts"
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/b7c73c1a-bd24-483d-884b-a9dd256f9eb9"
SITE_BASE_URL = "https://xzz-amu.github.io/engineering-learning"


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
    import os
    client = Anthropic(
        api_key=os.environ.get("ANTHROPIC_AUTH_TOKEN", os.environ.get("ANTHROPIC_API_KEY")),
        base_url=os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
    )
    system_prompt = (PROMPTS_DIR / "chapter-system-prompt.md").read_text()

    user_message = f"""请为以下知识点生成一篇教案：

## 知识点标题
{issue['title']}

## 学习目标和覆盖内容
{issue['body']}
"""

    response = client.messages.create(
        model=os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL", "claude-sonnet-4-6"),
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


def save_chapter(issue: dict, content: str) -> Path:
    """将生成的教案保存到文件。"""
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
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
    site_url = f"{SITE_BASE_URL}/chapters/{filepath.stem}/"
    comment = f"教案已生成！\n\n[点击阅读]({site_url})"
    subprocess.run(
        ["gh", "issue", "comment", str(issue_number), "--repo", REPO, "--body", comment],
        check=True
    )


def update_mkdocs_nav():
    """扫描 docs/chapters/ 目录，自动更新 mkdocs.yml 的 nav 配置。"""
    import yaml

    chapters = sorted(CHAPTERS_DIR.glob("*.md"))
    if not chapters:
        return

    mkdocs_path = PROJECT_DIR / "mkdocs.yml"
    with open(mkdocs_path) as f:
        config = yaml.safe_load(f)

    chapter_nav = []
    for ch in chapters:
        if ch.name == ".gitkeep":
            continue
        first_line = ch.read_text(encoding="utf-8").split("\n")[0]
        title = first_line.lstrip("# ").strip() if first_line.startswith("#") else ch.stem
        chapter_nav.append({title: f"chapters/{ch.name}"})

    config["nav"] = [
        {"首页": "index.md"},
        {"教案": chapter_nav}
    ]

    with open(mkdocs_path, "w") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def git_push():
    """Commit 并 push 生成的教案。"""
    subprocess.run(["git", "add", "docs/chapters/", "mkdocs.yml"], cwd=PROJECT_DIR, check=True)
    subprocess.run(
        ["git", "commit", "-m", "docs: auto-generate chapters"],
        cwd=PROJECT_DIR, check=True
    )
    subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True)


def send_feishu_notification(generated: list):
    """发送飞书通知。"""
    import requests

    if not generated:
        return

    chapter_lines = []
    for ch in generated:
        title = ch["title"]
        stem = Path(ch["path"]).stem
        url = f"{SITE_BASE_URL}/chapters/{stem}/"
        chapter_lines.append(f"[{title}]({url})")

    content = "\n".join(chapter_lines)

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "新教案已就绪"},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"今日教案已生成（共 {len(generated)} 篇）\n\n{content}"
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
        result = resp.json()
        if result.get("code") == 0:
            print("飞书通知发送成功")
        else:
            print(f"飞书通知发送失败: {result}")
    else:
        print(f"飞书通知发送失败: {resp.status_code} {resp.text}")


def main():
    issues = get_pending_issues()
    if not issues:
        print("没有待生成的 Issue，跳过。")
        return

    print(f"发现 {len(issues)} 个待生成的 Issue，开始生成...")
    generated = []
    for issue in issues:
        print(f"  正在生成: {issue['title']}...")
        content = generate_chapter(issue)
        filepath = save_chapter(issue, content)
        update_issue_label(issue["number"])
        comment_on_issue(issue["number"], filepath)
        generated.append({"title": issue["title"], "path": str(filepath)})
        print(f"  完成: {filepath}")

    update_mkdocs_nav()
    git_push()
    send_feishu_notification(generated)
    print(f"\n全部完成！共生成 {len(generated)} 篇教案，已 push 并发送飞书通知。")


if __name__ == "__main__":
    main()
