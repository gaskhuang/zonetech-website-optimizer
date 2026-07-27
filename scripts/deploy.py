#!/usr/bin/env python3
"""deploy.py — 從 GitHub Issue body 讀 WP 網址後部署"""
import json, os, base64, urllib.request, re, subprocess

WP_URL = "https://zonetech.tw/wp-json/wp/v2"
WP_TYPE = "blogs"
WP_USER = os.environ.get("WP_USER", "gask")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")

def wp_do(endpoint, data=None):
    headers = {"Authorization": f"Basic {base64.b64encode(f'{WP_USER}:{WP_PASS}'.encode()).decode()}",
               "Content-Type": "application/json",
               "User-Agent": "Mozilla/5.0 (compatible; ZoneTechDeploy/1.0)"}
    try:
        req = urllib.request.Request(f"{WP_URL}/{endpoint}", headers=headers,
            data=json.dumps(data).encode() if data else None, method="POST" if data else "GET")
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ❌ {e}")
        return None

def update_post(post_id, title=""):
    if not title:
        p = wp_do(f"{WP_TYPE}/{post_id}?_fields=id,title")
        if not p: return False
        title = p.get("title", {}).get("rendered", "")
    r = wp_do(f"{WP_TYPE}/{post_id}", {
        "meta": {"_seopress_titles_title": title,
                 "_seopress_titles_desc": f"{title[:60]} — 蓋斯克科技 ZoneTech"}})
    return bool(r)

print("=" * 50)
print("🚀 Auto Deploy — 讀 Issue body 網址")
test = wp_do(f"{WP_TYPE}?per_page=1&_fields=id")
if not test:
    print("❌ WP 連線失敗"); exit(1)
print(f"✅ WP 連線正常\n")

# 讀 GitHub 上 open 的 Issues
r = subprocess.run(["gh", "issue", "list", "--repo", "gaskhuang/zonetech-website-optimizer",
    "--state", "open", "--json", "number,title,body", "--limit", "30"],
    capture_output=True, text=True)
if r.returncode != 0:
    print("❌ gh issue list 失敗")
    exit(1)

issues = json.loads(r.stdout)
print(f"📋 找到 {len(issues)} 個 OPEN Issue\n")

ok = 0
for issue in issues:
    num = issue["number"]
    body = issue.get("body", "") or ""
    title = issue["title"]
    
    # 從 Issue body 抓網址 https://zonetech.tw/blogs/<slug>/
    urls = re.findall(r'https://zonetech\.tw/blogs/[a-z0-9-]+/', body)
    slugs = re.findall(r'/blogs/([a-z0-9-]+)', body)
    
    if urls:
        slug = slugs[0] if slugs else ""
        # 用 slug 查 WP post ID
        p = wp_do(f"{WP_TYPE}?slug={slug}&_fields=id,title") if slug else None
        if p and len(p) > 0:
            pid = p[0]["id"]
            print(f"  Issue #{num:2d} → {urls[0]} (Post {pid})", end="")
            if update_post(pid):
                print(" ✅"); ok += 1
                subprocess.run(["gh","issue","close",str(num),
                    "--repo","gaskhuang/zonetech-website-optimizer",
                    "-c","✅ WP 已更新"], capture_output=True)
            else:
                print(" ❌")
        else:
            print(f"  Issue #{num:2d} → {urls[0]} ⚠️ slug 找不到")
    else:
        print(f"  Issue #{num:2d} → ⏭️  無網址（批次/slug 型）")

print(f"\n✅ 總計 {ok} 項部署成功")
print("⚠️ 無網址的 Issue 下次開 Issue 時請加上網址")
