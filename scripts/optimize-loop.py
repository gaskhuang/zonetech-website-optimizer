#!/usr/bin/env python3
"""優化循環腳本 — 解析 tracking 報告 → 開 GitHub Issues（含 WP 網址）"""
import json, os, re, subprocess, sys, urllib.request
from datetime import datetime
from pathlib import Path

REPORT_DIR = Path(os.environ.get("HERMES_CRON_OUTPUT", os.path.expanduser("~/.hermes/cron/output")))

def parse_optimization_items():
    """從 tracking 報告提取優化項目"""
    reports = sorted(REPORT_DIR.glob("*website*tracking*"), reverse=True)
    if not reports:
        reports = sorted(REPORT_DIR.glob("*"), reverse=True)
    if not reports:
        print("❌ 無報告可解析")
        return []
    
    report = reports[0]
    print(f"📖 讀取：{report.name}")
    text = report.read_text(encoding="utf-8", errors="replace")
    
    # 找「優化項目」區塊
    items = []
    current_item = {}
    current_section = "一般"
    parse_sections = ["隱憂", "保養", "轉換", "待確認", "今日優化", "加速線路", "出口轉換"]
    is_parsing = False
    
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        
        # 偵測區段標題
        for section in parse_sections:
            if section in stripped:
                current_section = section
                if current_item.get("title"):
                    items.append(current_item)
                    current_item = {}
                continue
        
        # 遇到「資料狀態」「一週趨勢」等大標，結束 parse
        if re.match(r"^[一二三四五六七]、", stripped):
            if current_item.get("title"):
                items.append(current_item)
                current_item = {}
            if not any(m in stripped for m in parse_sections):
                is_parsing = False
            continue
        
        if not is_parsing:
            continue
        
        # 條列項目
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
    
    print(f"📋 解析到 {len(unique)} 個優化項目")
    for item in unique:
        print(f"  [{item['category']}] {item['urgency']} {item['title'][:60]}")
    return unique


def create_github_issue(item):
    title = f"[{item.get('category','一般')}] {item['title'][:90]}"
    
    # 從描述提取 slug → 組成 WP 網址
    desc = item.get('description', '')
    slug_m = re.search(r'[a-z][a-z0-9-]{4,60}[a-z0-9]', desc)
    post_url = f"https://zonetech.tw/blogs/{slug_m.group()}/\n" if slug_m else ''
    
    body = f"""## 優化項目

**文章網址：** {post_url}**類別：** {item.get('category', '一般')}
**緊急度：** {item.get('urgency', '中')}
**來源：** zonetech-website-tracking ({datetime.now().strftime('%Y-%m-%d')})

### 說明
{desc}

### 評分標準
- SEO 正確性 (0-100)
- 程式碼品質 (0-100)
- 效能影響 (0-100)
- 安全性 (0-100)
- 與網站風格一致 (0-100)

**通過門檻：** 總分 >= 85

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
        print(f"  >> Issue #{num} 已建立")
        return num, url
    else:
        print(f"  !! 建立失敗: {result.stderr[:100]}")
        return None, None


if __name__ == "__main__":
    items = parse_optimization_items()
    if not items:
        print("  >> 無優化項目，結束")
        sys.exit(0)
    
    issues = []
    for item in items:
        num, url = create_github_issue(item)
        if num:
            issues.append({"num": num, "url": url, "item": item})
    
    print(f"\n>> 共開 {len(issues)} 個 Issue")
    print(f"https://github.com/gaskhuang/zonetech-website-optimizer/issues")
    
    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "issues": [{"number": i["num"], "title": i["item"]["title"], "url": i["url"]} for i in issues]
    }
    output_path = Path("/tmp/optimizer_issues.json")
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n>> 結果已存：{output_path}")
