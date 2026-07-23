#!/usr/bin/env python3
"""完全重寫 deploy.py — 支援批次 Issue + 直接 Post ID 部署"""
import json, os, base64, urllib.request, re

WP_URL = "https://zonetech.tw/wp-json/wp/v2"
WP_TYPE = "blogs"
WP_USER = os.environ.get("WP_USER", "gask")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")

def wp_auth():
    t = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    return {"Authorization": f"Basic {t}", "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; ZoneTechOptimizer/1.0)"}

def wp_do(endpoint, data=None):
    headers = wp_auth()
    if data:
        req = urllib.request.Request(f"{WP_URL}/{endpoint}",
            data=json.dumps(data).encode(), headers=headers, method="POST")
    else:
        req = urllib.request.Request(f"{WP_URL}/{endpoint}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ❌ {e}")
        return None

# 直接 Post ID mapping
DIRECT = {
    19: 16224, 21: 14748, 24: 16407,
    3: 14856, 5: 14856, 6: 14779,
    13: 14886, 18: 14923, 23: 14695,
    25: 14680, 26: 14963,
    2: 15070, 9: 15518, 14: 15516,
    16: 15519, 17: 15005, 20: 15517, 22: 15517,
}

def deploy_post(post_id, issue_nums):
    """更新單一 WP post 的 SEOPress metadata"""
    post = wp_do(f"{WP_TYPE}/{post_id}?_fields=id,title")
    if not post:
        return False
    title = post.get("title", {}).get("rendered", "")
    result = wp_do(f"{WP_TYPE}/{post_id}", {
        "meta": {
            "_seopress_titles_title": title,
            "_seopress_titles_desc": f"{title[:60]} — 蓋斯克科技 ZoneTech"
        }
    })
    if result:
        print(f"  ✅ Post {post_id} 更新成功 (Issues: #{', #'.join(map(str, issue_nums))})")
        return True
    return False

print("=" * 60)
print("🚀 deploy.py v3 — 批次+直接部署")
print("=" * 60)

test = wp_do(f"{WP_TYPE}?per_page=1&_fields=id")
if not test:
    print("❌ WP 連線失敗")
    exit(1)
print(f"✅ WP 連線正常\n")

total_ok = 0

# Phase 1: 直接 Post ID 部署
print("📌 Phase 1: 直接 Post ID")
for issue_num, post_id in sorted(DIRECT.items()):
    print(f"  🚀 Issue #{issue_num:2d} → {WP_TYPE}/{post_id}")
    if deploy_post(post_id, [issue_num]):
        total_ok += 1

# Phase 2: 批次 Issue — 用關鍵字搜尋日期範圍內的文章
print("\n📌 Phase 2: 批次 (關鍵字比對)")
BATCH = {
    1:  ("7/5 批次", "2026-07-05"),
    4:  ("7/5 新文", "2026-07-05"),
    7:  ("07-10 五篇", "2026-07-10"),
    11: ("7/10 批次", "2026-07-10"),
}

# 搜尋近期文章
for issue_num, (label, date) in BATCH.items():
    print(f"  🚀 Issue #{issue_num:2d} ({label})")
    # 抓當天附近文章
    day = date.split("-")[-1]
    posts = wp_do(f"{WP_TYPE}?per_page=100&_fields=id,title,date&orderby=date&order=desc")
    if not posts:
        continue
    matched = []
    for p in posts:
        pdate = p.get("date", "")[:10]
        # 日期為該日前後 1 天內
        if date[:7] in pdate and abs(int(pdate.split("-")[-1]) - int(day)) <= 1:
            matched.append(p)
    if matched:
        print(f"    找到 {len(matched)} 篇 ({date} 附近)")
        for p in matched:
            if deploy_post(p["id"], []):
                total_ok += 1
    else:
        print(f"    ⚠️ 找不到 {date} 附近的文章")

print(f"\n✅ 總計: {total_ok} 項部署成功")
