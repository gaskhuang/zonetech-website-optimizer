#!/usr/bin/env python3
"""
🏭 蓋斯克網站每日優化 Loop — 主控制器

流程：
1. 讀取 zonetech-website-tracking 最新報告
2. 解析優化項目 → 開 GitHub Issues
3. 每個 Issue：Worker 修 → Picky 評分 → 未過就加 Worker → Advisor 審核 → 上線
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"
REPORT_DIR = Path(os.environ.get("HOME", "/tmp")) / ".hermes" / "cron" / "output"

# ─── 1. 解析追蹤報告 → 提取優化項目 ───
def parse_optimization_items():
    """
    從 zonetech-website-tracking 最新報告提取優化項目
    回傳 list of dict: {title, description, category, urgency}
    """
    # 找最新報告
    reports = sorted(REPORT_DIR.glob("*website*tracking*"), reverse=True)
    if not reports:
        print("⚠️ 找不到 zonetech-website-tracking 報告")
        # Fallback: 從今天 cron output 找
        reports = sorted(REPORT_DIR.glob("*"), reverse=True)

    if not reports:
        print("❌ 無報告可解析")
        return []

    latest = reports[0]
    print(f"📄 讀取報告：{latest.name}")
    content = latest.read_text(encoding="utf-8", errors="ignore")

    # 解析優化項目（從報告中提取行動車道項目）
    items = []
    lines = content.split("\n")
    in_action = False
    current_item = {}

    for line in lines:
        # 偵測「優化項目」區段
        if "優化項目" in line or "行動車道" in line or "accelerat" in line.lower() or "保養" in line:
            in_action = True
            continue
        if in_action and ("明天觀察" in line or "風險" in line or "資料狀態" in line):
            in_action = False
            continue

        if in_action and line.strip().startswith(("- ", "•", "*")):
            # 新項目
            if current_item.get("title"):
                items.append(current_item)
            current_item = {
                "title": line.strip().lstrip("- •*").strip()[:80],
                "description": line.strip().lstrip("- •*").strip(),
                "category": "優化",
                "urgency": "中"
            }
        elif in_action and current_item and line.strip():
            current_item["description"] += "\n" + line.strip()

    if current_item.get("title"):
        items.append(current_item)

    # 如果沒解析到，建立範例項目
    if not items:
        # 從全文找 actionable 內容
        for keyword in ["SEOPress", "metadata", "CTR", "曝光", "排名", "關鍵字", "blog", "文章"]:
            for i, line in enumerate(lines):
                if keyword.lower() in line.lower() and any(c in line for c in ["❌", "⚠️", "需", "應", "建議", "缺失"]):
                    items.append({
                        "title": line.strip()[:80],
                        "description": "\n".join(lines[max(0,i-1):min(len(lines),i+3)]).strip(),
                        "category": "自動偵測",
                        "urgency": "高" if "❌" in line else "中"
                    })
                    break

    # 去重
    seen = set()
    unique_items = []
    for item in items:
        key = item["title"][:40]
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    print(f"📋 解析到 {len(unique_items)} 個優化項目")
    return unique_items


# ─── 2. 開 GitHub Issue ───
def create_github_issue(item):
    """為每個優化項目開 GitHub Issue"""
    title = f"[優化] {item['title'][:100]}"
    body = f"""## 📋 優化項目

**類別：** {item.get('category', '一般')}
**緊急度：** {item.get('urgency', '中')}
**來源：** zonetech-website-tracking ({datetime.now().strftime('%Y-%m-%d')})

### 說明
{item['description']}

### 評分標準
- SEO 正確性 (0-100)
- 程式碼品質 (0-100)
- 效能影響 (0-100)
- 安全性 (0-100)
- 與網站風格一致 (0-100)

**通過門檻：** 總分 ≥ 85

### 狀態
- [ ] Worker 修復中
- [ ] Picky 評分中
- [ ] Advisor 審核中
- [ ] 已上線
"""
    cmd = [
        "gh", "issue", "create",
        "--repo", "gaskhuang/zonetech-website-optimizer",
        "--title", title,
        "--body", body,
        "--label", f"urgency:{item.get('urgency','中')}",
        "--label", "optimization"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        issue_url = result.stdout.strip()
        issue_num = issue_url.split("/")[-1]
        print(f"  ✅ Issue #{issue_num} 已建立")
        return issue_num, issue_url
    else:
        print(f"  ❌ 建立失敗：{result.stderr.strip()}")
        return None, None


# ─── 3. 主 Loop ───
def main():
    print("=" * 60)
    print(f"🏭 蓋斯克網站優化 Loop — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Step 1: 解析報告
    items = parse_optimization_items()
    if not items:
        print("📭 今日無優化項目，結束")
        return

    # Step 2: 開 Issues
    print("\n📋 開 GitHub Issues…")
    issues = []
    for item in items:
        num, url = create_github_issue(item)
        if num:
            issues.append({"num": num, "url": url, "item": item})

    print(f"\n✅ 共開 {len(issues)} 個 Issue")
    print(f"🔗 https://github.com/gaskhuang/zonetech-website-optimizer/issues")

    # Step 3: 輸出 Issue 清單（供後續 worker loop 使用）
    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "issues": [{"number": i["num"], "title": i["item"]["title"], "url": i["url"]} for i in issues]
    }
    output_path = Path("/tmp/optimizer_issues.json")
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n📝 Issue 清單已存：{output_path}")

    print("\n" + "=" * 60)
    print("🔧 下一步：Worker 開始修復（由 worker_picky_loop.py 執行）")
    print("=" * 60)


if __name__ == "__main__":
    main()