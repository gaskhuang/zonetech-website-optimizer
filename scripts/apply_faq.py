#!/usr/bin/env python3
"""將 FAQ (Elementor Toggle 風格) 寫入兩篇指定文章"""
import json, urllib.request, base64, re

WP_URL = "https://zonetech.tw/wp-json/wp/v2/blogs"
auth = base64.b64encode("gask:y3nk70VXgsh3Xe0qhd83JvQy".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json",
           "User-Agent": "ZoneTechFAQ/1.0"}

def wp_get(endpoint):
    req = urllib.request.Request(f"{WP_URL}/{endpoint}", headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def wp_post(endpoint, data):
    req = urllib.request.Request(f"{WP_URL}/{endpoint}",
        data=json.dumps(data).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

# FAQ HTML 模板（同 Elementor Toggle 視覺風格）
FAQ_CSS = """
<style>
.zt-faq { max-width: 800px; margin: 2em auto; }
.zt-faq-item { border-bottom: 1px solid #e0e0e0; }
.zt-faq-title {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 0; cursor: pointer;
  font-size: 16px; font-weight: 600; color: #1a1a2e;
  user-select: none;
}
.zt-faq-title:hover { color: #0056b3; }
.zt-faq-icon {
  width: 20px; height: 20px; flex-shrink: 0;
  transition: transform 0.3s ease; color: #0056b3;
}
.zt-faq-icon.open { transform: rotate(180deg); }
.zt-faq-content {
  max-height: 0; overflow: hidden;
  transition: max-height 0.3s ease, padding 0.3s ease;
  padding: 0 32px; color: #444; line-height: 1.8;
}
.zt-faq-content.open { max-height: 2000px; padding: 0 32px 20px; }
</style>
"""

# WiFi 滿格 FAQ
WIFI_FAQ = FAQ_CSS + """
<h2 style="font-size:24px;font-weight:700;color:#1a1a2e;margin-top:48px;border-left:4px solid #0056b3;padding-left:16px;">常見問題 Q&A</h2>
<div class="zt-faq">
<div class="zt-faq-item">
  <div class="zt-faq-title" onclick="this.nextElementSibling.classList.toggle('open');this.querySelector('.zt-faq-icon').classList.toggle('open');">
    <span class="zt-faq-icon">▼</span>
    <span>Q1：WiFi 滿格但很慢，一定是中華電信的問題嗎？</span>
  </div>
  <div class="zt-faq-content"><p>不一定。訊號滿格只代表你的裝置和 AP 之間連線良好，但上網速度還受到：AP 本身的效能瓶頸、同一台 AP 連了多少裝置、你用的頻段（2.4GHz vs 5GHz）、對外頻寬是否被吃滿等因素影響。<strong>建議先做我們文章裡的第 1-3 步自我排查</strong>，八成以上的問題不用花錢就能解決。</p></div>
</div>
<div class="zt-faq-item">
  <div class="zt-faq-title" onclick="this.nextElementSibling.classList.toggle('open');this.querySelector('.zt-faq-icon').classList.toggle('open');">
    <span class="zt-faq-icon">▼</span>
    <span>Q2：換 WiFi 7 路由器能解決「滿格但慢」的問題嗎？</span>
  </div>
  <div class="zt-faq-content"><p>不一定。如果瓶頸在對外頻寬不足、AP 擺放位置不對、或鄰近頻道干擾嚴重，換再好的 AP 也沒用。<strong>先排查再升級</strong>，才不會花冤枉錢。</p></div>
</div>
<div class="zt-faq-item">
  <div class="zt-faq-title" onclick="this.nextElementSibling.classList.toggle('open');this.querySelector('.zt-faq-icon').classList.toggle('open');">
    <span class="zt-faq-icon">▼</span>
    <span>Q3：我已經換了企業級 AP 還是慢，怎麼辦？</span>
  </div>
  <div class="zt-faq-content"><p>企業級 AP 需要正確的設定才能發揮效能。常見問題包括：頻道寬度沒調到 80/160MHz、未開啟 802.11r 快速漫遊、未做 Site Survey 導致 AP 布點不當。<strong>建議預約我們的免費到場檢測</strong>，工程師會用專業儀器幫您找出真正瓶頸。</p></div>
</div>
</div>
"""

# UniFi 最佳化 FAQ
UNIFI_FAQ = FAQ_CSS + """
<h2 style="font-size:24px;font-weight:700;color:#1a1a2e;margin-top:48px;border-left:4px solid #0056b3;padding-left:16px;">常見問題 Q&A</h2>
<div class="zt-faq">
<div class="zt-faq-item">
  <div class="zt-faq-title" onclick="this.nextElementSibling.classList.toggle('open');this.querySelector('.zt-faq-icon').classList.toggle('open');">
    <span class="zt-faq-icon">▼</span>
    <span>Q1：UniFi 和一般家用路由器差在哪？</span>
  </div>
  <div class="zt-faq-content"><p>UniFi 是企業級網管系統，支援集中管理（Controller/Cloud Key）、多 AP 無縫漫遊（802.11r/k/v）、 VLAN 隔離、訪客入口、頻寬管理等。<strong>家用路由器適合 1-2 台 AP、不須網管的場景；超過 3 台 AP 或需要資安分區就該用 UniFi。</strong></p></div>
</div>
<div class="zt-faq-item">
  <div class="zt-faq-title" onclick="this.nextElementSibling.classList.toggle('open');this.querySelector('.zt-faq-icon').classList.toggle('open');">
    <span class="zt-faq-icon">▼</span>
    <span>Q2：安裝 UniFi 後 WiFi 還是慢，最常見的原因是什麼？</span>
  </div>
  <div class="zt-faq-content"><p>前三名：<strong>① AP 布點位置不當</strong>（裝在天花板鐵皮後方）<strong>② 頻道未最佳化</strong>（沒用 DFS 頻道或相鄰 AP 同頻道打架）<strong>③ 未調整傳輸功率</strong>（功率太大反而造成同頻干擾）。文章中 10 大秘訣已經涵蓋這三項的解法。</p></div>
</div>
<div class="zt-faq-item">
  <div class="zt-faq-title" onclick="this.nextElementSibling.classList.toggle('open');this.querySelector('.zt-faq-icon').classList.toggle('open');">
    <span class="zt-faq-icon">▼</span>
    <span>Q3：我該找你們做 Site Survey 還是自己照文章設定？</span>
  </div>
  <div class="zt-faq-content"><p>如果 AP 數量在 5 台以下、環境單純（一般辦公室/店面），照文章設定即可改善 80% 問題。<strong>如果超過 5 台 AP、環境複雜（鐵皮屋/倉儲/多樓層）、或已經自行調整過仍無改善，建議預約我們的現場檢測。</strong>工程師會帶 Omnipeek 進階分析儀器，30 分鐘內找出問題。</p></div>
</div>
</div>
"""

# 部署
DEPLOY = [
    (14886, "wifi-full-bars-but-slow-2026", WIFI_FAQ),
    (14695, "unifi-wifi-optimization-guide", UNIFI_FAQ),
]

print("=" * 50)
for post_id, slug, faq_html in DEPLOY:
    post = wp_get(f"{post_id}?_fields=id,content")
    old_content = post["content"]["rendered"]
    
    # FAQ 已存在就不重複插入
    if "zt-faq" in old_content:
        print(f"  ⏭️ Post {post_id} ({slug}) — FAQ 已存在")
        continue
    
    new_content = old_content + "\n\n" + faq_html
    
    result = wp_post(f"{post_id}", {"content": new_content})
    if result:
        print(f"  ✅ Post {post_id} ({slug}) — FAQ 已寫入")
    else:
        print(f"  ❌ Post {post_id} — 寫入失敗")

print("=" * 50)
print("✅ 完成")
