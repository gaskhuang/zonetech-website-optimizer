#!/usr/bin/env python3
"""
🧠 L4 Hill Climbing Loop — Conclusion
分析過去一週的 trace → 優化 harness（worker 權重、picky 閾值、parse 規則）

角色：conclusion
模型：anthropic/claude-opus-4.8
排程：每週日 22:00
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO = "gaskhuang/zonetech-website-optimizer"
CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"


# ─── 1. 收集過去一週的 trace ───
def collect_weekly_traces(days=7):
    """從 GitHub Issues 收集過去 N 天的所有 trace"""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    cmd = [
        "gh", "issue", "list",
        "--repo", REPO,
        "--label", "optimization",
        "--since", since,
        "--state", "all",
        "--json", "number,title,labels,state,createdAt,closedAt,comments,body"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"❌ 讀取 Issues 失敗：{result.stderr}")
        return []

    issues = json.loads(result.stdout)
    print(f"📋 過去 {days} 天共 {len(issues)} 個 Issue")

    # 收集每個 Issue 的完整 trace
    traces = []
    for issue in issues:
        trace = {
            "number": issue["number"],
            "title": issue["title"],
            "state": issue["state"],
            "created": issue.get("createdAt", ""),
            "closed": issue.get("closedAt", ""),
            "labels": [l["name"] for l in issue.get("labels", [])],
            "comments_count": len(issue.get("comments", [])),
            "loops": 0,
            "workers": [],
            "scores": [],
            "final_score": None,
            "passed": "approved" in [l["name"] for l in issue.get("labels", [])]
        }

        # 從 comments 解析每輪分數
        for comment in issue.get("comments", []):
            body = comment.get("body", "")
            if "Picky 評分結果" in body or "picky" in body.lower():
                trace["loops"] += 1
                # 抓各 worker 分數
                for line in body.split("\n"):
                    for worker in ["deepseek", "chatgpt", "kimi", "qwen", "mimo", "minimax", "grok"]:
                        if worker in line.lower() and "/100" in line:
                            trace["workers"].append(worker)
            if "最高分" in body:
                import re
                m = re.search(r'(\d+\.?\d*)/100', body)
                if m:
                    trace["final_score"] = float(m.group(1))

        traces.append(trace)

    return traces


# ─── 2. 分析 pattern ───
def analyze_patterns(traces):
    """分析 trace pattern，回傳優化建議"""
    if not traces:
        return {"summary": "無資料", "optimizations": []}

    total = len(traces)
    passed = sum(1 for t in traces if t.get("passed"))
    failed = total - passed
    pass_rate = passed / total * 100 if total > 0 else 0

    # Worker 表現分析
    worker_scores = {}
    worker_types = {}
    for t in traces:
        title = t.get("title", "").lower()
        if "seo" in title or "meta" in title or "seopress" in title:
            issue_type = "SEO"
        elif "code" in title or "css" in title or "script" in title:
            issue_type = "程式碼"
        elif "content" in title or "文章" in title or "blog" in title:
            issue_type = "內容"
        else:
            issue_type = "一般"

        scores = t.get("scores", [])
        for s in scores:
            if s.get("worker"):
                w = s["worker"]
                if w not in worker_scores:
                    worker_scores[w] = {"total": 0, "count": 0, "types": {}}
                worker_scores[w]["total"] += s.get("score", 0)
                worker_scores[w]["count"] += 1
                if issue_type not in worker_scores[w]["types"]:
                    worker_scores[w]["types"][issue_type] = []
                worker_scores[w]["types"][issue_type].append(s.get("score", 0))

    # 計算平均
    worker_avg = {}
    for w, data in worker_scores.items():
        avg = data["total"] / data["count"] if data["count"] > 0 else 0
        worker_avg[w] = {"avg_score": round(avg, 1), "count": data["count"], "types": {}}
        for t, scores in data["types"].items():
            worker_avg[w]["types"][t] = round(sum(scores) / len(scores), 1) if scores else 0

    # 優化建議
    optimizations = []

    # 1. Worker 權重調整
    if worker_avg:
        best_worker = max(worker_avg.items(), key=lambda x: x[1]["avg_score"])
        worst_worker = min(worker_avg.items(), key=lambda x: x[1]["avg_score"])
        optimizations.append({
            "type": "worker_priority",
            "detail": f"最佳 Worker：{best_worker[0]} ({best_worker[1]['avg_score']}/100)，"
                      f"最差 Worker：{worst_worker[0]} ({worst_worker[1]['avg_score']}/100)",
            "action": f"提高 {best_worker[0]} 的優先順序，減少 {worst_worker[0]} 的調用"
        })

        # 2. Worker 專長分析
        for w, data in worker_avg.items():
            for t, score in data.get("types", {}).items():
                if score >= 90:
                    optimizations.append({
                        "type": "worker_specialty",
                        "detail": f"{w} 擅長 {t} 類問題（均分 {score}）",
                        "action": f"{t} 類 Issue 優先派給 {w}"
                    })

    # 3. 閾值分析
    if pass_rate < 50:
        optimizations.append({
            "type": "threshold_too_high",
            "detail": f"通過率僅 {pass_rate:.0f}%（{passed}/{total}）",
            "action": "考慮將 Picky 門檻從 85 降至 80，或檢討評分維度權重"
        })
    elif pass_rate > 90:
        optimizations.append({
            "type": "threshold_too_low",
            "detail": f"通過率高達 {pass_rate:.0f}%（{passed}/{total}）",
            "action": "考慮將 Picky 門檻從 85 提升至 90，以確保品質"
        })

    # 4. 循環次數分析
    loops = [t.get("loops", 0) for t in traces]
    avg_loops = sum(loops) / len(loops) if loops else 0
    if avg_loops > 2:
        optimizations.append({
            "type": "too_many_loops",
            "detail": f"平均每 Issue 需 {avg_loops:.1f} 輪才能通過",
            "action": "檢討 Worker prompt 品質，或增加首次 Worker 數量"
        })

    return {
        "summary": {
            "total_issues": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(pass_rate, 1),
            "avg_loops": round(avg_loops, 1),
            "worker_performance": worker_avg
        },
        "optimizations": optimizations
    }


# ─── 3. Conclusion：產生優化方案 ───
def conclusion_analyze(analysis):
    """Conclusion 分析 trace 並產出優化建議"""
    print(f"\n🧠 [Conclusion] 分析過去一週 trace…")
    print(f"  總 Issue：{analysis['summary']['total_issues']}")
    print(f"  通過率：{analysis['summary']['pass_rate']}%")
    print(f"  平均循環：{analysis['summary']['avg_loops']}")

    recommendations = []
    for opt in analysis["optimizations"]:
        recommendations.append({
            "type": opt["type"],
            "finding": opt["detail"],
            "recommendation": opt["action"]
        })

    # 如果通過率 > 80%，產生 config 更新建議
    config_updates = []
    if analysis["summary"]["pass_rate"] > 85:
        config_updates.append({
            "target": "scoring.pass_threshold",
            "current": 85,
            "suggested": 90,
            "reason": f"通過率 {analysis['summary']['pass_rate']}% 偏高，提升門檻確保品質"
        })
    elif analysis["summary"]["pass_rate"] < 40:
        config_updates.append({
            "target": "scoring.pass_threshold",
            "current": 85,
            "suggested": 80,
            "reason": f"通過率僅 {analysis['summary']['pass_rate']}%，降低門檻避免過度退回"
        })

    return {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "period": "過去 7 天",
        "summary": analysis["summary"],
        "recommendations": recommendations,
        "config_updates": config_updates,
        "analyzed_by": "conclusion (claude-opus-4.8)",
        "auto_optimized": len(config_updates) > 0
    }


# ─── 4. 更新 config ───
def apply_config_updates(report):
    """自動套用 config 更新"""
    if not report.get("config_updates"):
        print("📭 無需更新 config")
        return

    import yaml
    config = yaml.safe_load(CONFIG_PATH.read_text())
    
    for update in report["config_updates"]:
        # 支援 dot path
        keys = update["target"].split(".")
        target = config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = update["suggested"]
        print(f"  📝 更新 {update['target']}: {update['current']} → {update['suggested']}")

    CONFIG_PATH.write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True))
    print(f"  ✅ config 已更新")


# ─── 5. 產出週報 ───
def generate_report(report):
    """產出人類可讀的週報"""
    s = report["summary"]
    lines = [
        f"🧠 Conclusion 週報 — {report['report_date']}",
        f"",
        f"📊 本週成效",
        f"  Issue 總數：{s['total_issues']}",
        f"  通過審核：{s['passed']}（{s['pass_rate']}%）",
        f"  平均循環：{s['avg_loops']} 輪",
        f"",
    ]

    wp = s.get("worker_performance", {})
    if wp:
        lines.append(f"🤖 Worker 表現")
        for w, data in sorted(wp.items(), key=lambda x: -x[1]["avg_score"]):
            lines.append(f"  {w:20s} 均分 {data['avg_score']}/100（{data['count']} 次）")
        lines.append("")

    if report["recommendations"]:
        lines.append(f"💡 優化建議")
        for r in report["recommendations"]:
            lines.append(f"  • {r['finding']}")
            lines.append(f"    建議：{r['recommendation']}")
        lines.append("")

    if report.get("config_updates"):
        lines.append(f"⚙️ Config 自動更新")
        for u in report["config_updates"]:
            lines.append(f"  • {u['target']}: {u['current']} → {u['suggested']}")
        lines.append("")

    lines.append(f"分析者：{report['analyzed_by']}")
    return "\n".join(lines)


# ─── 主入口 ───
def main():
    print("=" * 60)
    print(f"🧠 L4 Hill Climbing Loop — Conclusion")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"🤖 模型：anthropic/claude-opus-4.8")
    print("=" * 60)

    # Step 1: 收集 trace
    print("\n📥 收集 trace…")
    traces = collect_weekly_traces(7)
    if not traces:
        print("📭 無 trace 資料，結束")
        return

    # Step 2: 分析 pattern
    print("\n🔍 分析 pattern…")
    analysis = analyze_patterns(traces)
    
    # 輸出分析結果
    print(f"\n📊 分析結果：")
    print(f"  總 Issue：{analysis['summary']['total_issues']}")
    print(f"  通過率：{analysis['summary']['pass_rate']}%")
    for opt in analysis["optimizations"]:
        print(f"  💡 {opt['type']}: {opt['detail'][:60]}…")

    # Step 3: Conclusion 產出優化方案
    print("\n🧠 Conclusion 分析中…")
    report = conclusion_analyze(analysis)

    # Step 4: 自動套用 config 更新
    print("\n⚙️ 自動優化…")
    apply_config_updates(report)

    # Step 5: 產出週報
    print("\n📝 產出週報…")
    report_text = generate_report(report)

    # 保存報告
    report_path = Path(f"/tmp/conclusion_weekly_report_{datetime.now().strftime('%Y%m%d')}.md")
    report_path.write_text(report_text)
    print(f"  ✅ 週報：{report_path}")

    # 開 GitHub Issue 作為週報
    title = f"[Conclusion] L4 優化週報 — {datetime.now().strftime('%Y-%m-%d')}"
    body = report_text
    cmd = [
        "gh", "issue", "create",
        "--repo", REPO,
        "--title", title,
        "--body", body,
        "--label", "conclusion",
        "--label", "weekly-report"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print(f"  ✅ 週報 Issue：{result.stdout.strip()}")
    else:
        print(f"  ⚠️ 開 Issue 失敗：{result.stderr}")

    print("\n" + "=" * 60)
    print("✅ Conclusion 完成")
    print("=" * 60)


if __name__ == "__main__":
    main()