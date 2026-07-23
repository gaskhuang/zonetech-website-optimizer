#!/usr/bin/env python3
"""FAQ v3 — 全行內樣式（無 style/script tag），inline onclick 控制展開收合"""
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

# 用 details/summary 才是 WordPress 安全的寫法
# + 補 CSS 到 style 區塊

FAQ_WIFI = """<h2 id="faq" style="font-size:24px;font-weight:700;color:#1a1a2e;margin-top:48px;border-left:4px solid #0056b3;padding-left:16px;">常見問題 Q&A</h2>
<div style="max-width:800px;margin:2em auto;">
<details style="border-bottom:1px solid #e0e0e0;padding:8px 0;">
<summary style="cursor:pointer;font-size:16px;font-weight:600;color:#1a1a2e;padding:8px 0;list-style:none;display:flex;align-items:center;gap:8px;"><span style="color:#0056b3;">▶</span> Q1：WiFi 滿格但很慢，一定是中華電信的問題嗎？</summary>
<p style="padding:8px 32px;color:#444;line-height:1.8;margin:0;">不一定。訊號滿格只代表你的裝置和 AP 之間連線良好，但上網速度還受到：AP 本身的效能瓶頸、同一台 AP 連了多少裝置、你用的頻段（2.4GHz vs 5GHz）、對外頻寬是否被吃滿等因素影響。<strong>建議先做我們文章裡的第 1-3 步自我排查</strong>，八成以上的問題不用花錢就能解決。</p>
</details>
<details style="border-bottom:1px solid #e0e0e0;padding:8px 0;">
<summary style="cursor:pointer;font-size:16px;font-weight:600;color:#1a1a2e;padding:8px 0;list-style:none;display:flex;align-items:center;gap:8px;"><span style="color:#0056b3;">▶</span> Q2：換 WiFi 7 路由器能解決嗎？</summary>
<p style="padding:8px 32px;color:#444;line-height:1.8;margin:0;">不一定。如果瓶頸在對外頻寬不足、AP 擺放位置不對、或鄰近頻道干擾嚴重，換再好的 AP 也沒用。<strong>先排查再升級</strong>，才不會花冤枉錢。</p>
</details>
<details style="border-bottom:1px solid #e0e0e0;padding:8px 0;">
<summary style="cursor:pointer;font-size:16px;font-weight:600;color:#1a1a2e;padding:8px 0;list-style:none;display:flex;align-items:center;gap:8px;"><span style="color:#0056b3;">▶</span> Q3：我已經換了企業級 AP 還是慢，怎麼辦？</summary>
<p style="padding:8px 32px;color:#444;line-height:1.8;margin:0;">企業級 AP 需要正確設定才能發揮效能。常見問題包括：頻道寬度沒調到 80/160MHz、未開啟 802.11r 快速漫遊、未做 Site Survey 導致 AP 布點不當。<strong>建議預約我們的免費到場檢測</strong>，工程師會用專業儀器幫您找出真正瓶頸。</p>
</details>
</div>"""

FAQ_UNIFI = """<h2 id="faq" style="font-size:24px;font-weight:700;color:#1a1a2e;margin-top:48px;border-left:4px solid #0056b3;padding-left:16px;">常見問題 Q&A</h2>
<div style="max-width:800px;margin:2em auto;">
<details style="border-bottom:1px solid #e0e0e0;padding:8px 0;">
<summary style="cursor:pointer;font-size:16px;font-weight:600;color:#1a1a2e;padding:8px 0;list-style:none;display:flex;align-items:center;gap:8px;"><span style="color:#0056b3;">▶</span> Q1：我已經安裝了 UniFi AP，為什麼 Wi-Fi 網速還是很慢？</summary>
<p style="padding:8px 32px;color:#444;line-height:1.8;margin:0;">網速慢通常不是 UniFi 設備本身的問題，而是設定未經最佳化。最常見的原因有三：一、AP 物理位置不佳，被障礙物遮擋；二、頻道設定錯誤，尤其 2.4GHz 頻段未選用互不干擾的 1、6、11 頻道；三、傳輸功率設為「高」，在多 AP 環境下造成「黏性客戶端」問題。建議從這三點著手檢查，通常能解決 80% 的效能問題。</p>
</details>
<details style="border-bottom:1px solid #e0e0e0;padding:8px 0;">
<summary style="cursor:pointer;font-size:16px;font-weight:600;color:#1a1a2e;padding:8px 0;list-style:none;display:flex;align-items:center;gap:8px;"><span style="color:#0056b3;">▶</span> Q2：UniFi 的 2.4GHz 和 5GHz 頻道寬度到底該怎麼設定？</summary>
<p style="padding:8px 32px;color:#444;line-height:1.8;margin:0;">2.4GHz 由於非常擁擠，應「永遠」設定為 20MHz。5GHz 若環境干擾低可設為 80MHz 追求極速；但在 AP 密集的企業辦公室，為了提升穩定性，將寬度縮減為 40MHz 是更專業的選擇。切忌在 2.4GHz 上使用 40MHz。</p>
</details>
<details style="border-bottom:1px solid #e0e0e0;padding:8px 0;">
<summary style="cursor:pointer;font-size:16px;font-weight:600;color:#1a1a2e;padding:8px 0;list-style:none;display:flex;align-items:center;gap:8px;"><span style="color:#0056b3;">▶</span> Q3：什麼是「黏性客戶端」問題？該如何解決？</summary>
<p style="padding:8px 32px;color:#444;line-height:1.8;margin:0;">「黏性客戶端」是指設備在辦公室移動時，即使旁邊有訊號更好的 AP，它仍然「黏」在原先連接的距離較遠的 AP 上不肯切換。解決方法：一、將所有 AP 的傳輸功率從「高」調降為「中」或「自動」；二、啟用「最低 RSSI」功能，設定 -75dBm 門檻，設備訊號低於此值時 AP 會主動將其踢除，迫使其重新連接到訊號更強的 AP。</p>
</details>
<details style="border-bottom:1px solid #e0e0e0;padding:8px 0;">
<summary style="cursor:pointer;font-size:16px;font-weight:600;color:#1a1a2e;padding:8px 0;list-style:none;display:flex;align-items:center;gap:8px;"><span style="color:#0056b3;">▶</span> Q4：UniFi 的 Channel AI 真的有用嗎？什麼時候該用？</summary>
<p style="padding:8px 32px;color:#444;line-height:1.8;margin:0;">Channel AI 對中小型辦公室非常有用，能每日凌晨自動掃描周遭環境，切換到干擾最少的頻道。但在 AP 密集的高密度環境，專業的手動頻道規劃通常能達到比 AI 更好的整體效能。此外，2.4GHz 建議永遠手動鎖定在 1、6、11 頻道。</p>
</details>
<details style="border-bottom:1px solid #e0e0e0;padding:8px 0;">
<summary style="cursor:pointer;font-size:16px;font-weight:600;color:#1a1a2e;padding:8px 0;list-style:none;display:flex;align-items:center;gap:8px;"><span style="color:#0056b3;">▶</span> Q5：自己調整跟請專業廠商做的差別在哪？</summary>
<p style="padding:8px 32px;color:#444;line-height:1.8;margin:0;">自行調整可解決基本問題，但專業廠商的價值在於「系統性診斷」與「客製化規劃」。我們會攜帶專業頻譜分析儀器到現場進行場勘，用數據找出實體干擾源和訊號死角，重新規劃 AP 最佳物理位置，並根據您的業務需求進行頻道、功率、VLAN 精細規劃。</p>
</details>
</div>"""

DEPLOY = [
    (14886, FAQ_WIFI, "wifi-full-bars"),
    (14695, FAQ_UNIFI, "unifi-wifi"),
]

print("=" * 50)
print("🚀 FAQ v3 — details/summary 純 HTML")
print("=" * 50)

for post_id, faq_html, label in DEPLOY:
    post = wp_get(f"{post_id}?_fields=id,content")
    content = post["content"]["rendered"]
    
    # 移除所有之前的 FAQ 痕跡
    content = re.sub(r'<style>[\s\S]*?</style>', '', content)
    content = re.sub(r'<script>[\s\S]*?</script>', '', content)
    content = re.sub(r'<div class="zt-faq"[^>]*>[\s\S]*?</div>\s*', '', content)
    content = re.sub(r'<details[\s\S]*?</details>\s*', '', content)
    content = re.sub(r'<h2[^>]*>常見問題 Q&A</h2>', '', content)
    content = re.sub(r'<!--[\s\S]*?-->', '', content)
    content = re.sub(r'\{[\s\S]*?"@type":[\s\S]*?"FAQPage"[\s\S]*?\}', '', content)
    
    new_content = content.strip() + "\n\n" + faq_html
    result = wp_post(f"{post_id}", {"content": new_content})
    if result:
        print(f"  ✅ Post {post_id} ({label}) — FAQ v3 已寫入")
    else:
        print(f"  ❌ Post {post_id} — 失敗")

print("=" * 50)
print("✅ 完成")
