#!/usr/bin/env python3
"""
🚀 上線腳本 — 將 Advisor 核准的修復部署到 zonetech.tw
透過 WP REST API + Application Password 寫入
"""

import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

WP_URL = "https://zonetech.tw/wp-json/wp/v2"
WP_USER = os.environ.get("WP_USER", "gask")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")

# ─── WP API 輔助 ───
def wp_auth_header():
    """回傳 Basic Auth header"""
    import base64
    token = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; ZoneTechOptimizer/1.0)"}


def wp_get(endpoint):
    """WP GET 請求"""
    req = urllib.request.Request(f"{WP_URL}/{endpoint}", headers=wp_auth_header())
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def wp_post(endpoint, data):
    """WP POST 請求（更新/建立）"""
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{WP_URL}/{endpoint}", data=body,
        headers=wp_auth_header(), method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.request.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


# ─── 實際部署 ───
DEPLOY_ACTIONS = {
    "seopress": lambda pid, fix: wp_post(f"posts/{pid}", {
        "meta": {
            "_seopress_titles_title": fix.get("title", ""),
            "_seopress_titles_desc": fix.get("description", "")
        }
    }),
    "slug": lambda pid, fix: wp_post(f"posts/{pid}", {
        "slug": fix.get("new_slug", "")
    }),
    "cta": lambda pid, fix: wp_post(f"posts/{pid}", {
        "content": fix.get("content", "")
    }),
    "content": lambda pid, fix: wp_post(f"posts/{pid}", {
        "content": fix.get("content", "")
    }),
}


def find_wp_post(issue_title):
    """從 Issue 標題找對應的 WP post"""
    import re
    # 抓常見 slug 模式：英文+數字+連字符組合（至少 5 字元）
    slugs = re.findall(r'[a-z][a-z0-9-]{4,}[a-z0-9]', issue_title.lower())
    for slug in slugs:
        result = wp_get(f"posts?slug={slug}&_fields=id,slug")
        if isinstance(result, list) and result:
            return result[0]["id"]
    # fallback: 用 slug 單字比對最新 30 篇
    result = wp_get("posts?per_page=30&_fields=id,title,slug")
    if isinstance(result, list):
        keywords = [w.lower() for w in re.findall(r'[a-z0-9-]{4,}', issue_title.lower())]
        for post in result:
            title = post.get("title", {}).get("rendered", "").lower()
            slug = post.get("slug", "").lower()
            if any(kw in title for kw in keywords) or any(kw == slug for kw in keywords):
                return post["id"]
    return None


def deploy_issue(issue_num, issue_title, fix_detail):
    """部署單一 Issue 的修復"""
    print(f"\n  🚀 Issue #{issue_num}: {issue_title[:50]}…")

    post_id = find_wp_post(issue_title)
    if not post_id:
        print(f"  ⚠️ 找不到對應 WP 文章，跳過")
        return False

    print(f"  📝 找到 WP post ID: {post_id}")

    # 根據 Issue 類型決定部署動作
    title_lower = issue_title.lower()
    action_type = "content"  # default

    if "seopress" in title_lower or "metadata" in title_lower:
        action_type = "seopress"
    elif "slug" in title_lower or "網址" in title_lower or "url" in title_lower:
        action_type = "slug"
    elif "cta" in title_lower or "轉換" in title_lower or "引導" in title_lower:
        action_type = "cta"

    fix = fix_detail if isinstance(fix_detail, dict) else {}
    result = DEPLOY_ACTIONS.get(action_type, DEPLOY_ACTIONS["content"])(post_id, fix)

    if "error" in result:
        print(f"  ❌ 部署失敗：{result['error'][:100]}")
        return False
    else:
        print(f"  ✅ Issue #{issue_num} 已部署上線（WP post #{post_id}）")
        return True


def main():
    print("=" * 60)
    print(f"🚀 上線部署 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    if not WP_PASS:
        print("❌ WP_APP_PASSWORD 未設定")
        print("   在 GitHub Secrets 設定：WP_USER + WP_APP_PASSWORD")
        return

    # 驗證 WP 連線
    test = wp_get("posts?per_page=1&_fields=id")
    if isinstance(test, dict) and "error" in test:
        print(f"❌ WP 連線失敗：{test['error'][:60]}")
        return
    print(f"✅ WP 連線正常")

    result_path = Path("/tmp/optimizer_daily_result.json")
    if not result_path.exists():
        print("📭 無今日結果，結束")
        return

    data = json.loads(result_path.read_text())
    approved = data.get("results", [])

    if not approved:
        print("📭 無通過項目需部署")
        return

    print(f"\n📋 待部署：{len(approved)} 項")
    success = 0
    for item in approved:
        if deploy_issue(item["issue"], item.get("title", ""), {}):
            success += 1

    print(f"\n✅ {success}/{len(approved)} 項部署成功")


if __name__ == "__main__":
    main()