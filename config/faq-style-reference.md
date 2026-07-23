# ✅ deploy 已完成（詳見上方）
# FAQ 風格分析與模板

## 從 WP REST API 抓到的 FAQ 結構

**文章 ID 16224**（it-outsourcing-guide-2026）使用 **Elementor Toggle Widget**。

### HTML 結構

```html
<!-- 容器 -->
<div class="elementor-widget-toggle" data-id="..." data-element_type="widget" 
     data-settings='{"selectors":{...},"toggle":"toggle"}'>
  <div class="elementor-widget-container">
    <div class="elementor-toggle">
      
      <!-- 單一 QA 項目 -->
      <div class="elementor-toggle-item">
        <div id="elementor-tab-title-xxx" class="elementor-tab-title" 
             data-tab="1" role="button" tabindex="0"
             aria-controls="elementor-tab-content-xxx">
          <span class="elementor-toggle-icon elementor-toggle-icon-xxx"
                aria-hidden="true">
            <i class="elementor-toggle-icon-opened fas fa-chevron-up"></i>
            <i class="elementor-toggle-icon-closed fas fa-chevron-down"></i>
          </span>
          <span class="elementor-toggle-title">Q1：問題標題</span>
        </div>
        <div id="elementor-tab-content-xxx" class="elementor-tab-content elementor-clearfix"
             data-tab="1" role="region"
             aria-labelledby="elementor-tab-title-xxx">
          <p>回答內容...</p>
        </div>
      </div>

      <!-- 後續 QA 類推，data-tab 遞增 -->
    </div>
  </div>
</div>
```

### CSS class 重點
| Class | 用途 |
|-------|------|
| `.elementor-widget-toggle` | 外層容器 |
| `.elementor-toggle` | toggle 清單 |
| `.elementor-toggle-item` | 單題 |
| `.elementor-tab-title` | 可點擊的題目行 |
| `.elementor-toggle-icon` | 箭頭圖示區 |
| `.elementor-toggle-icon-opened` | 展開時的箭頭（▲） |
| `.elementor-toggle-icon-closed` | 收合時的箭頭（▼） |
| `.elementor-toggle-title` | 題目文字 |
| `.elementor-tab-content` | 答案內容 |

### Style 規範
- Q 粗體 + 主題色
- ▼ 箭頭在左側，藍色
- 回答文字正常粗細
- 行距約 1.6
- 每題之間有間距

## 部署模板

已寫入 `scripts/faq_template.json` — Worker 可用此模板在文章底部插入 FAQ 區塊。

## 下一步
下次 Worker 修復文章時，會自動在文末補上這組 Elementor Toggle FAQ 結構。
