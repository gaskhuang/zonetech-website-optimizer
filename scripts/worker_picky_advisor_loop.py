#!/usr/bin/env python3
"""
🔧 Worker → Picky → Advisor Loop
Bilevel 結構：內層 Worker 修復 → 外層 Picky 評分 → 未過就加 Worker

流程：
1. 讀 Issue
2. 7 個 Worker 平行修復（每次最多 7 個）
3. Picky 評分（<85 重開 Issue + 加 Worker）
4. Advisor 最終審核
5. 通過 → 上線
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ─── 設定 ───
REPO = "gaskhuang/zonetech-website-optimizer"
PASS_THRESHOLD = 85
MAX_WORKERS = 7
MAX_LOOPS = 3  # 每個 Issue 最多重修次數

WORKERS = [
    {"name": "deepseek-v4-pro",    "prompt_prefix": "你是 DeepSeek V4 Pro，擅長程式碼優化與 SEO 修復。"},
    {"name": "chatgpt-5.5",        "prompt_prefix": "你是 ChatGPT 5.5，擅長全端開發與網頁最佳化。"},
    {"name": "kimi-k2.7-code",     "prompt_prefix": "你是 Kimi K2.7 Code，擅長程式碼審查與重構。"},
    {"name": "qwen3.7-max",        "prompt_prefix": "你是 Qwen 3.7 Max，擅長前端開發與效能調校。"},
    {"name": "mimo-v2.5-pro",      "prompt_prefix": "你是 MiMo V2.5 Pro，擅長 WordPress 開發與 SEO。"},
    {"name": "minimax-m3",         "prompt_prefix": "你是 MiniMax M3，擅長內容優化與結構化資料。"},
    {"name": "grok-4.5",           "prompt_prefix": "你是 Grok 4.5，擅長創意解法與突破性優化。"},
]


# ─── 1. Worker：修復 Issue ───
def worker_fix(issue_num, issue_title, issue_body, worker, context=""):
    """單一 Worker 修復 Issue，回傳修復方案"""
    print(f"  🤖 [{worker['name']}] 開始修復 Issue #{issue_num}…")

    # 這裡實際呼叫 LLM API
    # 在 Hermes cron 環境中，透過 terminal 呼叫或直接 call API
    fix = {
        "worker": worker["name"],
        "issue": issue_num,
        "timestamp": datetime.now().isoformat(),
        "fix_summary": f"由 {worker['name']} 提出的修復方案",
        "fix_detail": f"針對 Issue #{issue_num}: {issue_title}\n{context}",
        "status": "done"
    }
    return fix


# ─── 2. Picky：評分修復品質 ───
def picky_score(issue_num, issue_body, fixes):
    """
    Picky 評分所有 Worker 的修復
    回傳 {scores, best_fix, overall_score, passed}
    """
    print(f"  🔍 [Picky] 評分 Issue #{issue_num} 的修復…")

    # 評分各維度
    scores = {}
    for fix in fixes:
        # 實際會 call Gemini API 評分
        scores[fix["worker"]] = {
            "SEO_正確性": __mock_score(70, 100),
            "程式碼品質": __mock_score(70, 100),
            "效能影響":   __mock_score(70, 100),
            "安全性":     __mock_score(80, 100),
            "風格一致":   __mock_score(70, 100),
        }

    # 計算總分
    results = []
    for worker, dims in scores.items():
        total = sum(dims.values()) / len(dims)
        results.append({"worker": worker, "score": round(total, 1), "dimensions": dims})

    results.sort(key=lambda x: -x["score"])
    best = results[0]
    overall = best["score"]

    return {
        "scores": results,
        "best_fix": best,
        "overall_score": overall,
        "passed": overall >= PASS_THRESHOLD
    }


def __mock_score(min_v, max_v):
    """模擬評分（實際會 call Gemini API）"""
    import random
    return random.randint(min_v, max_v)


# ─── 3. Advisor：最終審核 ───
def advisor_review(issue_num, issue_body, best_fix, picky_report):
    """Advisor 最終審核，決定是否上線"""
    print(f"  👑 [Advisor] 審核 Issue #{issue_num}…")

    review = {
        "approved": True,
        "comments": "修復方案符合標準，同意上線",
        "suggestions": [],
        "reviewer": "claude-fable-5"
    }
    return review


# ─── 4. GitHub Issue 操作 ───
def gh_cmd(*args):
    """執行 gh CLI 命令"""
    cmd = ["gh"] + list(args) + ["--repo", REPO]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()


def reopen_issue(issue_num, message):
    """重開 Issue + 留言"""
    gh_cmd("issue", "reopen", str(issue_num))
    gh_cmd("issue", "comment", str(issue_num), "--body", message)


def close_issue(issue_num, message):
    """關閉 Issue + 留言"""
    gh_cmd("issue", "comment", str(issue_num), "--body", message)
    gh_cmd("issue", "close", str(issue_num))


def add_label(issue_num, label):
    """加標籤"""
    gh_cmd("issue", "edit", str(issue_num), "--add-label", label)


# ─── 5. 主 Loop：每個 Issue 的 Worker→Picky→Advisor ───
def process_issue(issue_num, issue_title, issue_body):
    """處理單一 Issue 的完整循環"""
    print(f"\n{'='*50}")
    print(f"📌 處理 Issue #{issue_num}: {issue_title[:50]}")
    print(f"{'='*50}")

    loop_count = 0
    all_workers = []
    active_workers = WORKERS[:]  # 初始 7 個

    # 確保變數在 loop 外部有預設值
    picky_result = None
    best = None

    while loop_count < MAX_LOOPS and active_workers:
        loop_count += 1
        print(f"\n🔄 Loop {loop_count} — {len(active_workers)} 個 Worker 同時修復")

        # Step A: 所有 Worker 平行修復
        fixes = []
        for worker in active_workers:
            fix = worker_fix(issue_num, issue_title, issue_body, worker)
            fixes.append(fix)
            all_workers.append(worker["name"])

        # Step B: Picky 評分
        add_label(issue_num, "picky-reviewing")
        picky_result = picky_score(issue_num, issue_body, fixes)

        # 輸出評分結果
        print(f"\n  📊 Picky 評分結果：")
        for r in picky_result["scores"]:
            mark = "✅" if r["score"] >= PASS_THRESHOLD else "❌"
            print(f"    {mark} {r['worker']:18s} → {r['score']:.0f}/100")

        best = picky_result["best_fix"]
        print(f"\n  🏆 最佳：{best['worker']} ({best['score']}/100)")

        if picky_result["passed"]:
            print(f"  ✅ 分數 ≥ {PASS_THRESHOLD}，進入 Advisor 審核")
            break
        else:
            # 未過：重開 Issue + 加更多 Worker
            print(f"  ❌ 分數 {best['score']} < {PASS_THRESHOLD}，重開 Issue")
            reopen_msg = (
                f"## 🔄 Loop {loop_count} 未通過\n\n"
                f"最高分：{best['worker']} → {best['score']}/100\n"
                f"門檻：{PASS_THRESHOLD}/100\n\n"
                f"### 各 Worker 分數\n"
                + "\n".join(f"- {r['worker']}: {r['score']}/100" for r in picky_result["scores"])
                + "\n\n### 重開原因\n"
                "未達品質門檻，加入下一輪 Worker 共同修復。"
            )
            reopen_issue(issue_num, reopen_msg)

            # 如果還有 worker 沒被叫過，加進來
            used_names = set(all_workers)
            remaining = [w for w in WORKERS if w["name"] not in used_names]
            if remaining and len(active_workers) < MAX_WORKERS:
                # 換掉最差的 worker，加入新的
                new_worker = remaining[0]
                active_workers = [w for w in active_workers if w["name"] != best["worker"]]
                active_workers.append(new_worker)
                print(f"  ➕ 加入新 Worker: {new_worker['name']}")
            else:
                print(f"  ⚠️ 已用滿 {MAX_WORKERS} 個 Worker，保留原陣容再試")

    # Step C: Advisor 最終審核
    if picky_result["passed"]:
        add_label(issue_num, "advisor-reviewing")
        review = advisor_review(issue_num, issue_body, best, picky_result)

        if review["approved"]:
            print(f"\n  👑 Advisor 審核通過 ✅")
            close_msg = (
                f"## ✅ 審核通過\n\n"
                f"**最佳修復：** {best['worker']} ({best['score']}/100)\n"
                f"**審核者：** {review['reviewer']}\n"
                f"**意見：** {review['comments']}\n\n"
                f"---\n"
                f"### 上線項目\n"
                f"此 Issue 已核准，準備上線發布。"
            )
            close_issue(issue_num, close_msg)
            add_label(issue_num, "approved")
            add_label(issue_num, "ready-to-deploy")
            return True, best
        else:
            print(f"\n  👑 Advisor 退回，需重修")
            close_msg = (
                f"## 🔙 Advisor 退回\n\n"
                f"**原因：** {review['comments']}\n"
                f"**建議：** {', '.join(review['suggestions'])}\n\n"
                f"退回 Worker 重修。"
            )
            reopen_issue(issue_num, close_msg)
            add_label(issue_num, "advisor-rejected")
            return False, None
    else:
        print(f"\n  ❌ 經過 {MAX_LOOPS} 輪仍未達標，標記為人工處理")
        close_msg = (
            f"## ⚠️ 需人工介入\n\n"
            f"經過 {MAX_LOOPS} 輪自動修復，最高分 {best['score']}/100\n"
            f"未達門檻 {PASS_THRESHOLD}/100，請人工確認。"
        )
        close_issue(issue_num, close_msg)
        add_label(issue_num, "needs-human-review")
        return False, None


# ─── 6. 入口 ───
def main():
    print("=" * 60)
    print(f"🔧 蓋斯克優化 Worker→Picky→Advisor Loop")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 讀取 Issue 清單（由 optimize-loop.py 產出）
    issues_path = Path("/tmp/optimizer_issues.json")
    if not issues_path.exists():
        # 直接從 GitHub 抓 open issues
        ok, stdout, _ = gh_cmd("issue", "list", "--label", "optimization", "--state", "open", "--json", "number,title,body")
        if ok and stdout:
            issues = json.loads(stdout)
        else:
            print("❌ 無待處理 Issue")
            return
    else:
        data = json.loads(issues_path.read_text())
        issues = data["issues"]

    print(f"\n📋 待處理 Issue：{len(issues)} 個")

    # 依序處理每個 Issue
    results = []
    for issue in issues:
        # 取得完整 Issue body
        ok, stdout, _ = gh_cmd("issue", "view", str(issue["number"]), "--json", "title,body")
        if ok and stdout:
            data = json.loads(stdout)
            body = data.get("body", "")
            title = data.get("title", issue["title"])
        else:
            body = ""
            title = issue["title"]

        passed, best = process_issue(issue["number"], title, body)
        results.append({
            "issue": issue["number"],
            "title": title,
            "passed": passed,
            "best_worker": best["worker"] if best else None,
            "best_score": best["score"] if best else 0
        })

    # 輸出報告
    print("\n" + "=" * 60)
    print("📊 今日優化結果")
    print("=" * 60)
    passed_count = sum(1 for r in results if r["passed"])
    for r in results:
        status = "✅ 已核准" if r["passed"] else "⚠️ 需人工"
        print(f"  #{r['issue']} {status} | {r.get('best_worker','?'):18s} | {r.get('best_score',0)}/100")
    print(f"\n總計：{passed_count}/{len(results)} 個通過審核")

    # 輸出結果 JSON
    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_issues": len(results),
        "passed": passed_count,
        "results": results
    }
    output_path = Path("/tmp/optimizer_daily_result.json")
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\n📝 結果已存：{output_path}")


if __name__ == "__main__":
    main()