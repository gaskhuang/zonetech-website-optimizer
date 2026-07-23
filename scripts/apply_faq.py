#!/usr/bin/env python3
"""FAQ v5 — 對齊 Elementor Toggle 視覺大小"""
import json, urllib.request, base64

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

# 對齊 Elementor Toggle 視覺
FAQ = """<h2 style="font-family:system-ui,-apple-system,sans-serif;font-size:22px;font-weight:700;color:#1a1a2e;margin-top:48px;margin-bottom:24px;border-left:4px solid #0056b3;padding-left:16px;">更多關於 UniFi 最佳化全攻略的常見問題FAQ</h2>
<div style="max-width:800px;margin:0 auto;">
<details style="border-bottom:1px solid #e8e8e8;padding:0;">
<summary style="cursor:pointer;font-family:system-ui,-apple-system,sans-serif;font-size:15px;font-weight:600;color:#1a1a2e;list-style-type:none;padding:14px 16px;margin:0;display:flex;align-items:center;gap:10px;">&#9660; Q1：我已經安裝了 UniFi AP，為什麼 Wi-Fi 網速還是很慢？</summary>
<div style="padding:4px 16px 16px 32px;font-family:system-ui,-apple-system,sans-serif;font-size:14px;color:#555;line-height:1.7;"><p style="margin:0;">網速慢通常不是 UniFi 設備本身的問題，而是設定未經最佳化。最常見的原因有三：一、AP 物理位置不佳，被障礙物遮擋；二、頻道設定錯誤，尤其 2.4GHz 頻段未選用互不干擾的 1、6、11 頻道；三、傳輸功率設為「高」，在多 AP 環境下造成「黏性客戶端」問題。建議從這三點著手檢查，通常能解決 80% 的效能問題。</p></div>
</details>
<details style="border-bottom:1px solid #e8e8e8;padding:0;">
<summary style="cursor:pointer;font-family:system-ui,-apple-system,sans-serif;font-size:15px;font-weight:600;color:#1a1a2e;list-style-type:none;padding:14px 16px;margin:0;display:flex;align-items:center;gap:10px;">&#9660; Q2：UniFi 的 2.4GHz 和 5GHz 頻道寬度到底該怎麼設定？</summary>
<div style="padding:4px 16px 16px 32px;font-family:system-ui,-apple-system,sans-serif;font-size:14px;color:#555;line-height:1.7;"><p style="margin:0;">2.4GHz 由於非常擁擠，應「永遠」設定為 20MHz。5GHz 若環境干擾低可設為 80MHz 追求極速；但在 AP 密集的企業辦公室，為了提升穩定性，將寬度縮減為 40MHz 是更專業的選擇。切忌在 2.4GHz 上使用 40MHz。</p></div>
</details>
<details style="border-bottom:1px solid #e8e8e8;padding:0;">
<summary style="cursor:pointer;font-family:system-ui,-apple-system,sans-serif;font-size:15px;font-weight:600;color:#1a1a2e;list-style-type:none;padding:14px 16px;margin:0;display:flex;align-items:center;gap:10px;">&#9660; Q3：什麼是「黏性客戶端」問題？該如何解決？</summary>
<div style="padding:4px 16px 16px 32px;font-family:system-ui,-apple-system,sans-serif;font-size:14px;color:#555;line-height:1.7;"><p style="margin:0;">「黏性客戶端」是指設備在辦公室移動時，即使旁邊有訊號更好的 AP，它仍然「黏」在原先連接的距離較遠的 AP 上不肯切換。解決方法：一、將所有 AP 的傳輸功率從「高」調降為「中」或「自動」；二、啟用「最低 RSSI」功能，設定 -75dBm 門檻，設備訊號低於此值時 AP 會主動將其踢除，迫使其重新連接到訊號更強的 AP。</p></div>
</details>
<details style="border-bottom:1px solid #e8e8e8;padding:0;">
<summary style="cursor:pointer;font-family:system-ui,-apple-system,sans-serif;font-size:15px;font-weight:600;color:#1a1a2e;list-style-type:none;padding:14px 16px;margin:0;display:flex;align-items:center;gap:10px;">&#9660; Q4：UniFi 的 Channel AI 真的有用嗎？什麼時候該用？</summary>
<div style="padding:4px 16px 16px 32px;font-family:system-ui,-apple-system,sans-serif;font-size:14px;color:#555;line-height:1.7;"><p style="margin:0;">Channel AI 對中小型辦公室非常有用，能每日凌晨自動掃描周遭環境，切換到干擾最少的頻道。但在 AP 密集的高密度環境，專業的手動頻道規劃通常能達到比 AI 更好的整體效能。此外，2.4GHz 建議永遠手動鎖定在 1、6、11 頻道。</p></div>
</details>
<details style="border-bottom:1px solid #e8e8e8;padding:0;">
<summary style="cursor:pointer;font-family:system-ui,-apple-system,sans-serif;font-size:15px;font-weight:600;color:#1a1a2e;list-style-type:none;padding:14px 16px;margin:0;display:flex;align-items:center;gap:10px;">&#9660; Q5：自己調整跟請專業廠商做的差別在哪？</summary>
<div style="padding:4px 16px 16px 32px;font-family:system-ui,-apple-system,sans-serif;font-size:14px;color:#555;line-height:1.7;"><p style="margin:0;">自行調整可解決基本問題，但專業廠商的價值在於「系統性診斷」與「客製化規劃」。我們會攜帶專業頻譜分析儀器到現場進行場勘，用數據找出實體干擾源和訊號死角，重新規劃 AP 最佳物理位置，並根據您的業務需求進行頻道、功率、VLAN 精細規劃。</p></div>
</details>
</div>"""

for post_id in [14886, 14695]:
    post = wp_get(f"{post_id}?_fields=id,content")
    content = post["content"]["rendered"]
    idx = content.rfind('常見問題')
    if idx > 0:
        base = content[:content.rfind('<h2', 0, idx)]
    else:
        base = content
    # 也更新 WiFi 文章
    if post_id == 14886:
        faq_use = FAQ.replace('UniFi 最佳化全攻略', 'WiFi 滿格卻很慢 2026')
    else:
        faq_use = FAQ
    result = wp_post(f"{post_id}", {"content": base.strip() + '\n\n' + faq_use})
    print(f"  {'✅' if result else '❌'} Post {post_id}")

print("✅ 完成")
