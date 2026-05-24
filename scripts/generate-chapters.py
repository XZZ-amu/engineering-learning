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

    mkdocs_path = Path("mkdocs.yml")
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

    update_mkdocs_nav()

    # 输出生成结果供后续步骤使用
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"generated={json.dumps(generated, ensure_ascii=False)}\n")
            f.write(f"count={len(generated)}\n")


if __name__ == "__main__":
    main()
