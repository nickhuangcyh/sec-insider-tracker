## 為什麼 (Why)

內部人交易（SEC Form 4）申報提供了市場情緒和潛在股價波動的重要信號。然而，手動從 SEC EDGAR 系統獲取並解析這些數據既複雜又耗時。本項目旨在建立一個低成本、自動化的追蹤系統，以易於閱讀的格式呈現這些信號。

## 變更內容 (What Changes)

- **自動化數據流水線**：一個每日運行的 GitHub Actions 工作流，用於獲取新的申報文件。
- **Python 數據抓取器**：利用 `edgartools` 庫將 Form 4 XML 數據解析為結構化的 JSON。
- **按日期分檔存儲**：倉庫中的 `data/` 目錄將按日期存儲每日交易（如 `2024-05-16.json`），並維護一個 `index.json` 索引，僅保留最近 180 天的數據檔案。
- **靜態網頁介面**：部署在 GitHub Pages 的網站（Vanilla JS/Tailwind），透過讀取索引文件並加載每日 JSON 數據，將其渲染為可搜索、可排序的表格。

## 能力 (Capabilities)

### 新增能力 (New Capabilities)
- `insider-data-fetcher`：用於獲取、解析和過濾 SEC Form 4 申報文件的 Python 邏輯。
- `data-rolling-storage`：在靜態 JSON 文件中合併每日更新並維護滾動 6 個月交易歷史的策略。
- `insider-tracker-ui`：一個輕量級的靜態前端，用於視覺化追蹤內部人交易。

### 修改能力 (Modified Capabilities)
- （無 - 這是新項目的初始設置）

## 影響 (Impact)

- **代碼倉庫**：在 `scripts/`、`.github/workflows/` 和 `web/` 中新增文件。
- **依賴項**：新增用於數據抓取的 `edgartools`。
- **CI/CD**：GitHub Actions 將定期進行 Commit 以更新數據文件。
