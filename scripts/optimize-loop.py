#!/usr/bin/env python3
"""
🏭 蓋斯克網站每日優化 Loop — 主控制器

流程：
1. 讀取 zonetech-website-tracking 最新報告
2. 解析優化項目（隱憂/保養/出口轉換/確認項目 → 全納入）
3. 開 GitHub Issues
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

REPORT_DIR = Path(os.environ.get("HOME", "/tmp")) / ".hermes" / "cron" / "output"

# 報告區段關鍵字
SECTION_MARKERS = {
    "優化項目": "優化",
    "行動車道": "優化",
    "保養": "維護",
    "加速": "優化",
    "出口": "轉換",
    "轉換": "轉換",
    "風險": "風險",
    "隱憂": "風險",
    "確認": "待確認",
    "觀察": "待確認",
    "急修": "急修",
}


def detect_section(line):
    """偵測當前是哪個區段"""
    for kw, cat in SECTION_MARKERS.items():
        if kw in line:
            return cat
    return None


def parse_optimization_items():
    """
    從 zonetech-website-tracking 最新報告提取優化項目
    涵蓋：隱憂、保養、出口轉換、待確認項目 → 全部開 Issue
    """
    reports = sorted(REPORT_DIR.glob("*website*tracking*"), reverse=True)
    if not reports:
        reports = sorted(REPORT_DIR.glob("*"), reverse=True)
    if not reports:
        print("❌ 無報告可解析")
        return []

    latest = reports[0]
    print(f"📄 讀取報告：{latest.name}")
    content = latest.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")

    items = []
    current_section = "一般"
    current_item = {}

    # 區段關鍵字：進到這些區段就開始擷取
    parse_sections = [
        "優化項目", "行動車道", "保養車道", "加速線路",
        "出口", "轉換", "風險", "隱憂", "異常",
        "需要確認", "觀察", "急修"
    ]

    is_parsing = False

    for line in lines:
        stripped = line.strip()

        # 偵測區段標題
        detected = False
        for marker in parse_sections:
            if marker in line:
                current_section = detect_section(line) or "一般"
                # 特殊開關：出口/轉換/風險/隱憂/異常 也要進 parse
                if any(m in line for m in ["保養", "加速", "出口", "轉換", "風險", "隱憂", "異常", "優化項目", "行動車道", "急修", "需要確認", "觀察"]):
                    is_parsing = True
                detected = True
                break

        if detected:
            # 關閉上一個 item
            if current_item.get("title"):
                items.append(current_item)
                current_item = {}
            continue

        # 遇到「資料狀態」「一週趨勢」等大標，結束 parse
        if is_parsing and re.match(r"^[一二三四五六七]、", line):
            if current_item.get("title"):
                items.append(current_item)
                current_item = {}
            if not any(m in line for m in parse_sections):
                is_parsing = False
            continue

        if not is_parsing:
            continue

        # 擷取條列項目
        if stripped.startswith(("- ", "•", "*")) or re.match(r"^\d+[.、]", stripped):
            if current_item.get("title"):
                items.append(current_item)

            title_text = re.sub(r"^[-•*\d.、\s]+", "", stripped).strip()
            urgency = "高" if any(c in stripped for c in ["❌", "⚠️", "急", "🆘"]) else \
                     "中" if "需" in stripped or "應" in stripped else "低"

            current_item = {
                "title": title_text[:100],
                "description": stripped,
                "category": current_section,
                "urgency": urgency
            }
        elif current_item and stripped:
            current_item["description"] += "\n" + stripped

    # 最後一個 item
    if current_item.get("title"):
        items.append(current_item)

    # 去重
    seen = set()
    unique = []
    for item in items:
        key = item["title"][:40]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    print(f"📋 解析到 {len(unique)} 個優化項目（含隱憂/保養/轉換/確認）")
    for item in unique:
        print(f"  [{item['category']}] {item['urgency']} {item['title'][:60]}")
    return unique


def create_github_issue(item):
    title = f"[{item.get('category','一般')}] {item['title'][:90]}"
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
        "--label", f"category:{item.get('category','一般')}",
        "--label", "optimization"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        url = result.stdout.strip()
        num = url.split("/")[-1]
        print(f"  ✅ Issue #{num} 已建立")
        return num, url
    else:
        print(f"  ❌ 建立失敗：{result.stderr.strip()}")
        return None, None


def main():
    print("=" * 60)
    print(f"🏭 蓋斯克網站優化 Loop — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    items = parse_optimization_items()
    if not items:
        print("📭 今日無優化項目，結束")
        return

    print(f"\n📋 開 GitHub Issues…")
    issues = []
    for item in items:
        num, url = create_github_issue(item)
        if num:
            issues.append({"num": num, "url": url, "item": item})

    print(f"\n✅ 共開 {len(issues)} 個 Issue")
    print(f"🔗 https://github.com/gaskhuang/zonetech-website-optimizer/issues")

    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "issues": [{"number": i["num"], "title": i["item"]["title"], "url": i["url"]} for i in issues]
    }
    output_path = Path("/tmp/optimizer_issues.json")
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n📝 Issue 清單已存：{output_path}")

    print("\n" + "=" * 60)
    print("🔧 下一步：Worker 開始修復（由 worker_picky_advisor_loop.py 執行）")
    print("=" * 60)


if __name__ == "__main__":
    main()