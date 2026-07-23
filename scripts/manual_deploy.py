#!/usr/bin/env python3
"""手動部署 Issue→WP 對照表 — 給 GitHub Actions 用"""
import json, os, base64, urllib.request

WP_URL = "https://zonetech.tw/wp-json/wp/v2"
WP_USER = os.environ.get("WP_USER", "gask")
WP_PASS = os.environ.get("WP_APP_PASSWORD", "")

def wp_auth():
    t = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    return {"Authorization": f"Basic {t}", "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; ZoneTechOptimizer/1.0)"}

def wp_post(endpoint, data):
    req = urllib.request.Request(f"{WP_URL}/{endpoint}",
        data=json.dumps(data).encode(), headers=wp_auth(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ❌ {e}")
        return None

def wp_get(endpoint):
    req = urllib.request.Request(f"{WP_URL}/{endpoint}", headers=wp_auth())
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ❌ {e}")
        return None

# Issue → WP post ID（從 WP Admin 截圖比對）
MAPPING = {
    3:  "有線回程 vs 無線回程",      # wired-vs-wireless-mesh
    5:  "有線回程 vs 無線回程",
    6:  "WiFi無縫漫遊｜LINE通話不斷線", # connection-breaking
    9:  "SSD vs HDD",                 # ssd-vs-hdd
    13: "WiFi 滿格卻很慢",            # wifi-full-bars
    14: "資訊安全三要素 CIA",          # information-security-cia
    16: "系統整合 SI",                # system-integration
    17: "企業網路建置",               # network-construction
    18: "4K 影片剪輯電腦",            # 4k-editing-pc
    19: "IT 委外 2026",              # it-outsourcing-guide
    20: "寬頻斷線排查",              # isp-broadband-disconnection
    21: "AP-on-a-stick",             # ap-on-a-stick
    22: "寬頻斷線排查",              # isp-broadband-disconnection
    23: "UniFi Wi-Fi 最佳化",        # unifi-wifi-optimization
    24: "UniFi 區域防火牆",          # unifi-zone-based-firewall
    25: "Mesh Wi-Fi 適合選購",       # mesh-wifi-enterprise-purchase
    26: "GMI Cloud AI Factory",      # gmi-cloud-ai-factory
}

print("=" * 60)
print("🚀 手動 Issue → WP 部署")
print("=" * 60)

# Step 1: 用關鍵字搜尋 WP 找 post ID
found = {}
for post in wp_get("posts?per_page=100&_fields=id,title,slug&orderby=date&order=desc"):
    t = f"{post['title']['rendered']} {post['slug']}"
    for issue_num, keyword in MAPPING.items():
        if keyword.lower() in t.lower():
            found.setdefault(post['id'], []).append(issue_num)

print(f"\n找到 {len(found)} 篇對應文章：")
for pid, issues in sorted(found.items()):
    print(f"  Post {pid} → Issue #{', #'.join(map(str, sorted(issues)))}")

# Step 2: 部署（SEOPress metadata）
for pid, issues in sorted(found.items()):
    print(f"\n  🚀 Post {pid} (Issues: #{', #'.join(map(str, sorted(issues)))})")
    post = wp_get(f"posts/{pid}?_fields=id,title")
    if not post:
        continue
    title = post.get("title", {}).get("rendered", "")
    result = wp_post(f"posts/{pid}", {
        "meta": {
            "_seopress_titles_title": title,
            "_seopress_titles_desc": f"{title} — 蓋斯克科技 ZoneTech"
        }
    })
    if result:
        print(f"  ✅ 已更新 SEOPress metadata")

print(f"\n✅ 部署完成")
