# 🏭 蓋斯克網站每日優化 Loop

每日追蹤報告 → 自動開 Issue → 7 模型 Worker 修復 → Picky 評分 → Advisor 審核 → 上線

## 流程

```
📊 zonetech-website-tracking (每日 06:00)
        │
        ▼ 產出優化項目
📋 自動開 GitHub Issues
        │
        ▼ 每個 Issue 進入 Worker Loop
🔧 Workers (7 模型同時修)
   ├── deepseek/deepseek-v4-pro
   ├── openai/chatgpt-5.5
   ├── moonshotai/kimi-k2.7-code
   ├── qwen/qwen3.7-max
   ├── xiaomi/mimo-v2.5-pro
   ├── minimax/minimax-m3
   └── x-ai/grok-4.5
        │
        ▼ 提交修復
🔍 Picky (google/gemini-3.5-flash) 評分
        │
        ├── 分數 ≥ 85 → Advisor 審核
        │
        └── 分數 < 85 → 重開 Issue + 再加 Worker (最多 7 個同時)
        │
        ▼
👑 Advisor (anthropic/claude-fable-5) 最終審核
        │
        ├── 通過 → 上線發布
        │
        └── 退回 → 回 Worker 重修
```

## 角色

| 角色 | 模型 | 職責 |
|------|------|------|
| Worker | 7 模型平行 | 根據 Issue 修復網站問題 |
| Picky | gemini-3.5-flash | 評分修復品質 (<85 退回) |
| Advisor | claude-fable-5 | 最終審核 + 上線批准 |

## 觸發

- 自動：每天 zonetech-website-tracking cron 完成後
- 手動：`gh workflow run daily-optimizer.yml`