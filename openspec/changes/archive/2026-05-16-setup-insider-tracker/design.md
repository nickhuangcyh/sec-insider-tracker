## 上下文 (Context)

本項目旨在建立一個基於 GitHub Pages 的靜態網站，用於追蹤 SEC Form 4 內部人交易。由於 GitHub Pages 不支持動態數據庫，我們將利用 GitHub Actions 作為自動化後端，每日抓取數據並以靜態 JSON 檔案的形式存儲在倉庫中。

## 目標 / 非目標 (Goals / Non-Goals)

**目標：**
- 實現每日自動化抓取 SEC Form 4 數據。
- 採用「每日一檔」的存儲策略，保證數據的可擴展性與快取效率。
- 提供一個輕量級的 Web 界面供用戶瀏覽最近 180 天的交易。
- 嚴格遵守 SEC 的 API 使用規範（User-Agent, 限速）。
- **提供基礎搜尋功能**：在前端實現關鍵字搜尋（如職位、姓名、代碼）。

**非目標：**
- 不提供歷史數據的長期存檔（僅保留 180 天）。
- 不提供複雜的用戶賬戶或個性化訂閱功能。
- 不進行實時數據抓取（僅每日更新）。
- **不實現數據分頁**：初步預計單日交易量不會超過瀏覽器處理上限，MVP 階段不開發分頁功能。

## 技術決策 (Decisions)

### 1. 目錄結構
為了保持項目整潔，我們將採用以下目錄佈局：
- `scripts/`: 存放 Python 抓取與處理腳本。
- `data/`: 存放每日 JSON 檔案及 `index.json` 索引。
- `web/`: 存放前端 HTML/JS/CSS 代碼（部署至 GitHub Pages）。
- `.github/workflows/`: 存放 GitHub Actions YAML 設定。

### 2. 數據格式 (JSON Schema)
**索引檔案 (`data/index.json`)：**
```json
[
  "2024-05-16",
  "2024-05-15",
  "..."
]
```

**每日數據檔案 (`data/2024-05-16.json`)：**
```json
{
  "date": "2024-05-16",
  "transactions": [
    {
      "ticker": "NVDA",
      "insider": "Huang Jen Hsun",
      "type": "S",
      "shares": 120000,
      "price": 905.2,
      "value": 108624000,
      "url": "..."
    }
  ]
}
```

### 3. 自動化流程 (GitHub Actions)
- **觸發機制**：每日定時執行（例如 UTC 00:00）或手動觸發。
- **流程步驟**：
    1. Checkout 倉庫代碼。
    2. 安裝 Python 依賴（`edgartools`）。
    3. 執行 Python 腳本：抓取昨日/今日數據 -> 生成新 JSON -> 更新 `index.json` -> 清理舊檔案。
    4. 自動 Commit 並 Push 變更至倉庫。

### 4. 前端讀取策略
- 前端使用原生 `fetch` API。
- 先加載 `index.json` 獲取日期列表。
- 根據用戶選擇（默認最新）加載對應的日期檔案。
- 使用 Tailwind CSS (CDN 版) 進行快速樣式開發，減少構建步驟。
- **搜尋實現**：採用前端即時過濾（Client-side filtering），利用 JavaScript 的 `filter` 方法對加載的 JSON 數據進行關鍵字比對。

## 風險 / 權衡 (Risks / Trade-offs)

- **[風險] GitHub Actions Commit 過多** → **[對策]** 這是預期的行為，且數據檔案很小。為了避免主分支雜亂，可以考慮將數據存儲在獨立的分支（如 `gh-pages` 或 `data` 分支），但為了簡化起見，初期先放在主分支。
- **[風險] SEC API 限速或格式變動** → **[對策]** `edgartools` 已處理大部分解析邏輯。若格式大改，需手動更新腳本。
- **[權衡] 靜態分片 vs 單一檔案** → **[選擇]** 選擇靜態分片。雖然增加了檔案數量，但大幅提升了前端加載大數據集時的性能與快取效率。

## 未決問題 (Open Questions)

- (目前暫無未決問題)
