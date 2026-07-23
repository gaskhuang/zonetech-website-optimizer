#!/usr/bin/env python3
"""手動部署 v2 — 用直接 Post ID 寫入 WP（blogs 自訂文章類型）"""
import json, os, base64, urllib.request

WP_URL = "https://zonetech.tw/wp-json/wp/v2"
WP_TYPE = "blogs"
WP_USER = os.environ.get("WP_USER", "gask")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")

def wp_auth():
    t = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    return {"Authorization": f"Basic {t}", "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; ZoneTechDeploy/1.0)"}

def wp_req(endpoint, data=None):
    headers = wp_auth()
    if data:
        req = urllib.request.Request(f"{WP_URL}/{endpoint}", data=json.dumps(data).encode(), headers=headers, method="POST")
    else:
        req = urllib.request.Request(f"{WP_URL}/{endpoint}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ❌ HTTP {e.code}: {body[:80]}")
        return None
    except Exception as e:
        print(f"  ❌ {e}")
        return None

DEPLOY = [
    (19, 16224, "seopress", "IT 委外 2026"),
    (21, 14748, "seopress", "AP-on-a-stick"),
    (24, 16407, "seopress", "UniFi 區域防火牆"),
    (3,  14856, "meta", "有線回程 vs 無線回程"),
    (5,  14856, "meta", "有線回程 vs 無線回程"),
    (6,  14779, "meta", "WiFi無縫漫遊"),
    (13, 14886, "meta", "WiFi 滿格卻很慢"),
    (18, 14923, "meta", "4K 剪輯電腦採購"),
    (23, 14695, "meta", "UniFi Wi-Fi 最佳化"),
    (25, 14680, "meta", "Mesh Wi-Fi 選購"),
    (26, 14963, "meta", "GMI Cloud AI Factory"),
    (2,  15070, "meta", "MikroTik 防火牆"),
    (9,  15518, "meta", "SSD vs HDD"),
    (14, 15516, "meta", "資訊安全 CIA"),
    (16, 15519, "meta", "系統整合 SI"),
    (17, 15005, "meta", "企業網路建置"),
    (20, 15517, "meta", "寬頻斷線"),
    (22, 15517, "meta", "寬頻斷線標題"),
]

print("=" * 60)
print(f"🚀 手動部署 — {WP_TYPE}/ 共 {len(DEPLOY)} 項")
print("=" * 60)

test = wp_req(f"{WP_TYPE}?per_page=1&_fields=id")
if not test:
    print("❌ WP 連線失敗")
    exit(1)
print(f"✅ WP 連線正常\n")

ok = 0
for issue_num, post_id, action, desc in DEPLOY:
    print(f"  🚀 Issue #{issue_num:2d} → {WP_TYPE}/{post_id} ({desc})")
    post = wp_req(f"{WP_TYPE}/{post_id}?_fields=id,title")
    if not post:
        print(f"  ⚠️  找不到")
        continue
    title = post.get("title", {}).get("rendered", "")
    result = wp_req(f"{WP_TYPE}/{post_id}", {
        "meta": {
            "_seopress_titles_title": title,
            "_seopress_titles_desc": f"{title[:60]} — 蓋斯克科技 ZoneTech"
        }
    })
    if result:
        print(f"  ✅")
        ok += 1

print(f"\n✅ {ok}/{len(DEPLOY)} 部署成功")
