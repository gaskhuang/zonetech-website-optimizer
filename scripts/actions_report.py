#!/usr/bin/env python3
"""產生 Actions 彙總報告（從 log 檔讀取）"""
import json
from pathlib import Path

report = []
report.append("## 🏭 每日優化 Loop 結果\n")

# Step 1 log
log1 = Path("/tmp/opt_step1.log")
if log1.exists():
    report.append("### Step 1: 解析報告")
    report.append("```")
    report.append(log1.read_text().strip())
    report.append("```\n")

# Step 2 log
log2 = Path("/tmp/opt_step2.log")
if log2.exists():
    report.append("### Step 2: Worker→Picky→Advisor")
    report.append("```")
    report.append(log2.read_text().strip())
    report.append("```\n")

# 結果 JSON
result_file = Path("/tmp/optimizer_daily_result.json")
if result_file.exists():
    report.append("### 通過狀態")
    data = json.loads(result_file.read_text())
    for r in data.get("results", []):
        s = "✅" if r.get("passed") else "⚠️"
        report.append(f"- {s} #{r['issue']} | {r.get('best_worker','?')} | {r.get('best_score',0)}/100")
    report.append(f"總計: {data.get('passed',0)}/{data.get('total_issues',0)} 通過")
else:
    report.append("(尚無結果)")

print("\n".join(report))