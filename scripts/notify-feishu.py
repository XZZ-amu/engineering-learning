#!/usr/bin/env python3
"""通过飞书 webhook 推送教案生成通知。"""

import os
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

    chapter_lines = []
    for ch in generated_chapters:
        title = ch["title"]
        path = ch["path"]
        stem = path.replace("docs/chapters/", "").replace(".md", "")
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
                    "content": f"今日教案已生成（共 {len(generated_chapters)} 篇）\n\n{content}"
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
    generated_json = os.environ.get("GENERATED_CHAPTERS", "[]")
    generated = json.loads(generated_json)
    send_notification(generated)


if __name__ == "__main__":
    main()
