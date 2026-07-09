# 🏭 蓋斯克網站每日優化 Loop

四層循環架構（LangChain 框架），從自動化執行到自動進化。

## 四層架構

```
┌─────────────────────────────────────────────────────────────┐
│  L4  Hill Climbing Loop  🧠 Conclusion (claude-opus-4.8)   │
│  trace → 分析 → 優化 harness（worker 權重/picky 閾值）    │
│  每週日 22:00                                              │
├─────────────────────────────────────────────────────────────┤
│  L3  Event-Driven Loop  ⏰ Cron / Webhook                   │
│  06:00 tracking → 06:30 optimizer → 07:00 GitHub Actions    │
│  每週日 22:00 Conclusion                                    │
├─────────────────────────────────────────────────────────────┤
│  L2  Verification Loop  🔍 Picky (gemini-3.5-flash)         │
│  產出 → grader 評分 → <85 retry+feedback → ≥85 下一關      │
├─────────────────────────────────────────────────────────────┤
│  L1  Agent Loop  🤖 7 Workers 平行修復                      │
│  LLM + tools → 重複直到任務完成                             │
└─────────────────────────────────────────────────────────────┘
```

## 流程

```
📊 zonetech-website-tracking (每日 06:00)
        │
        ▼ 產出優化項目
📋 自動開 GitHub Issues (06:30)
        │
        ▼ 每個 Issue 進入 L1+L2 Loop
┌─ L1 ──────────────────────────────────────┐
│  🔧 Workers (7 模型同時修)                 │
│   ├── deepseek/deepseek-v4-pro             │
│   ├── openai/chatgpt-5.5                   │
│   ├── moonshotai/kimi-k2.7-code            │
│   ├── qwen/qwen3.7-max                     │
│   ├── xiaomi/mimo-v2.5-pro                 │
│   ├── minimax/minimax-m3                   │
│   └── x-ai/grok-4.5                        │
└────────────────────────────────────────────┘
        │
┌─ L2 ──────────────────────────────────────┐
│  🔍 Picky (gemini-3.5-flash) 評分          │
│                                            │
│  ├── ✅ 分數 ≥ 85 → Advisor 審核          │
│  └── ❌ 分數 < 85 → 重開 Issue + 加 Worker │
│       （最多 7 個同時，最多 3 輪）          │
└────────────────────────────────────────────┘
        │
┌─ L3 ──────────────────────────────────────┐
│  👑 Advisor (claude-fable-5) 最終審核      │
│  ├── ✅ 通過 → 上線發布                    │
│  └── 🔙 退回 → 回 Worker 重修             │
└────────────────────────────────────────────┘
        │
        ▼ 上線發布
```

```
每週日 22:00 ── L4 Hill Climbing Loop
        │
┌─ L4 ──────────────────────────────────────┐
│  🧠 Conclusion (claude-opus-4.8)           │
│                                            │
│  1. 讀過去 7 天所有 Issue trace            │
│  2. 分析 pattern：                         │
│     - 哪個 Worker 擅長哪類問題             │
│     - Picky 閾值是否合理                   │
│     - 哪些 Issue 類型 consistently 修不好  │
│  3. 自動優化：                             │
│     - 調整 Worker 配權重                   │
│     - 調整 Picky 評分閾值                  │
│     - 更新 parse 規則                     │
│  4. 產出週報 + 開 Issue                    │
└────────────────────────────────────────────┘
```

## 角色

| 層級 | 角色 | 模型 | 職責 |
|------|------|------|------|
| L1 | Worker (×7) | deepseek-v4-pro / chatgpt-5.5 / kimi-k2.7-code / qwen3.7-max / mimo-v2.5-pro / minimax-m3 / grok-4.5 | 修復 Issue |
| L2 | Picky | google/gemini-3.5-flash | 評分修復品質 (<85 退回) |
| L3 | Advisor | anthropic/claude-fable-5 | 最終審核 + 上線批准 |
| L4 | Conclusion | anthropic/claude-opus-4.8 | 每週 trace 分析 + 系統優化 |

## 觸發時間

| 時間 | 事件 | 說明 |
|------|------|------|
| 06:00 | zonetech-website-tracking | 產出每日 SEO/流量報告 |
| 06:30 | website-optimizer cron | 解析報告 → 開 GitHub Issues |
| 07:00 | GitHub Actions (daily-optimizer) | Worker→Picky→Advisor 循環 |
| 22:00 (每週日) | Conclusion cron | L4 Hill Climbing 分析 |

## Repo

```
github.com/gaskhuang/zonetech-website-optimizer
├── .github/
│   ├── workflows/
│   │   ├── daily-optimizer.yml        # 每日 L1+L2+L3
│   │   └── l4-conclusion-weekly.yml  # 每週 L4
│   └── ISSUE_TEMPLATE/optimization.md
├── scripts/
│   ├── optimize-loop.py               # L1: 開 Issues
│   ├── worker_picky_advisor_loop.py   # L1+L2+L3: 修復→評分→審核
│   ├── conclusion_l4.py               # L4: Hill Climbing 分析
│   └── deploy.py                      # 上線
├── config/
│   └── settings.yaml                  # 設定（會自動進化）
└── README.md
```