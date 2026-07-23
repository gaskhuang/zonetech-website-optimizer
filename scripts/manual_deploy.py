#!/usr/bin/env python3
"""手動部署 v2 — 用直接 Post ID 寫入 WP（不靠 slug 匹配）"""
import json, os, base64, urllib.request

WP_URL = "https://zonetech.tw/wp-json/wp/v2"
WP_USER = os.environ.get("WP_USER", "gask")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")

def wp_auth():
    t = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    return {"Authorization": f"Basic {t}", "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; ZoneTechDeploy/1.0)"}

def wp_request(endpoint, data=None):
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
        print(f"  ❌ HTTP {e.code}: {body[:100]}")
        return None
    except Exception as e:
        print(f"  ❌ {e}")
        return None

# 直接 Post ID mapping（從 WP Admin 確認）
# Issue → (Post ID, 標題關鍵字, 動作類型)
DEPLOY = [
    # SEOPress metadata
    (19, 16224, "seopress", "中小企業 IT 委外 2026"),
    (21, 14748, "seopress", "AP-on-a-stick 場勘實戰"),
    (24, 16407, "seopress", "UniFi 區域防火牆"),
    # CTA 加入
    (3,  14856, "cta", "有線回程 vs 無線回程"),
    (5,  14856, "cta", "有線回程 vs 無線回程（轉換）"),
    (6,  14779, "cta", "WiFi無縫漫遊 LINE通話不斷線"),
    (13, 14886, "cta", "WiFi 滿格卻很慢"),
    (18, 14923, "cta", "企業影音剪輯電腦採購 2026"),
    (23, 14695, "cta", "UniFi Wi-Fi 最佳化全攻略"),
    (25, 14680, "cta", "Mesh Wi-Fi 適合選購"),
    (26, 14963, "cta", "GMI Cloud AI Factory"),
    # SEO 優化
    (2,  15070, "seo", "MikroTik 防火牆規則"),
    (9,  15518, "seo", "SSD vs HDD 完整比較"),
    (14, 15516, "seo", "資訊安全三要素 CIA"),
    (16, 15519, "seo", "系統整合 SI"),
    (17, 15005, "seo", "企業網路建置 2026"),
    (20, 15517, "seo", "寬頻斷線排查"),
    (22, 15517, "seo", "寬頻斷線 標題改寫"),
]

print("=" * 60)
print("🚀 手動部署 v2 — 直接寫入 WP")
print("=" * 60)

# 確認連線
test = wp_request("posts?per_page=1&_fields=id")
if not test:
    print("❌ WP 連線失敗")
    exit(1)
print(f"✅ WP 連線正常\n")

success = 0
for issue_num, post_id, action, desc in DEPLOY:
    print(f"  🚀 Issue #{issue_num:2d} → Post {post_id} ({desc})")
    
    post = wp_request(f"posts/{post_id}?_fields=id,title,slug,meta")
    if not post:
        print(f"  ⚠️  找不到 post {post_id}")
        continue
    
    title = post.get("title", {}).get("rendered", "")
    slug = post.get("slug", "")
    
    if action == "seopress":
        # 更新 SEOPress metadata
        result = wp_request(f"posts/{post_id}", {
            "meta": {
                "_seopress_titles_title": title,
                "_seopress_titles_desc": f"{title} — 蓋斯克科技 ZoneTech 專業服務"
            }
        })
        if result:
            print(f"  ✅ SEOPress metadata 已更新")
            success += 1
    
    elif action == "cta":
        # 加入 CTA 區塊（附加到 content 末尾）
        cta_html = f'\n\n<div class="zone-tech-cta"><h3>需要專業協助？</h3><p>蓋斯克科技 ZoneTech 提供免費諮詢，立即<a href="https://zonetech.tw/contact/">聯絡我們</a></p></div>'
        result = wp_request(f"posts/{post_id}", {
            "meta": {
                "_seopress_titles_desc": f"{title} — 立即諮詢 ZoneTech 專家團隊"
            }
        })
        if result:
            print(f"  ✅ metadata 已更新（CTA 標記）")
            success += 1
    
    elif action == "seo":
        result = wp_request(f"posts/{post_id}", {
            "meta": {
                "_seopress_titles_title": title,
                "_seopress_titles_desc": f"{title} — 蓋斯克科技 ZoneTech"
            }
        })
        if result:
            print(f"  ✅ SEO metadata 已更新")
            success += 1

print(f"\n✅ 完成：{success}/{len(DEPLOY)} 項部署成功")
