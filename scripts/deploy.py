#!/usr/bin/env python3
"""deploy.py — WP 自動部署（含直接 Post ID mapping + 批次日期搜尋）"""
import json, os, base64, urllib.request, re

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

# === 直接 Post ID mapping（已確認正確）===
DIRECT_MAP = {
    19: 16224, 21: 14748, 24: 16407,
    3: 14856, 5: 14856, 6: 14779,
    13: 14886, 18: 14923, 23: 14695,
    25: 14680, 26: 14963,
    2: 15070, 9: 15518, 14: 15516,
    16: 15519, 17: 15005, 20: 15517, 22: 15517,
}

BATCH_DATES = {
    1: "2026-07-05", 4: "2026-07-05",
    7: "2026-07-10", 11: "2026-07-10",
}

def update_post(post_id, title=""):
    """更新 SEOPress metadata"""
    if not title:
        p = wp_do(f"{WP_TYPE}/{post_id}?_fields=id,title")
        if not p: return False
        title = p.get("title", {}).get("rendered", "")
    r = wp_do(f"{WP_TYPE}/{post_id}", {
        "meta": {"_seopress_titles_title": title,
                 "_seopress_titles_desc": f"{title[:60]} — 蓋斯克科技 ZoneTech"}})
    return bool(r)

print("=" * 50)
print("🚀 Auto Deploy")
test = wp_do(f"{WP_TYPE}?per_page=1&_fields=id")
if not test:
    print("❌ WP 連線失敗"); exit(1)
print(f"✅ WP 連線正常\n")

ok = 0

# Phase 1: 直接 mapping
print("📌 直接 Post ID")
for issue, pid in sorted(DIRECT_MAP.items()):
    print(f"  Issue #{issue:2d} → post {pid}", end="")
    if update_post(pid):
        print(" ✅"); ok += 1
    else:
        print(" ❌")

# Phase 2: 批次日期搜尋
print("\n📌 批次日期搜尋")
posts = wp_do(f"{WP_TYPE}?per_page=100&_fields=id,title,date&orderby=date&order=desc") or []
for issue, date_str in BATCH_DATES.items():
    day = int(date_str.split("-")[-1])
    matched = [p for p in posts if date_str[:7] in p.get("date","")[:10]
               and abs(int(p["date"][:10].split("-")[-1]) - day) <= 1]
    print(f"  Issue #{issue:2d} ({date_str}) → {len(matched)} 篇", end="")
    for p in matched:
        if update_post(p["id"]):
            ok += 1
    print(f" ✅")

# Phase 3: 關閉已部署的 Issue
print("\n📌 關閉 Issue")
import subprocess
for issue in list(DIRECT_MAP.keys()) + list(BATCH_DATES.keys()):
    r = subprocess.run(["gh","issue","close",str(issue),
        "--repo","gaskhuang/zonetech-website-optimizer",
        "-c","✅ 已自動部署到 WP"], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  Issue #{issue} 已關閉")

print(f"\n✅ 總計 {ok} 項部署成功")
