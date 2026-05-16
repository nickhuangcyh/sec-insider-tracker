## 1. 項目環境初始化

- [x] 1.1 建立項目目錄結構 (`scripts/`, `data/`, `web/`, `.github/workflows/`)
- [x] 1.2 撰寫 `requirements.txt` 並包含 `edgartools`
- [x] 1.3 初始化 `data/index.json` 為空列表 `[]`

## 2. 後端抓取與處理腳本 (Python)

- [x] 2.1 實作 `scripts/fetch_insider_data.py`：使用 `edgartools` 獲取當日 Form 4 申報
- [x] 2.2 實作數據解析邏輯：從 XML 提取代碼、內部人、金額等關鍵欄位
- [x] 2.3 實作存儲邏輯：生成 `YYYY-MM-DD.json` 並更新 `index.json`
- [x] 2.4 實作清理邏輯：確保 `index.json` 僅保留 180 筆記錄並刪除對應的舊檔案

## 3. GitHub Actions 自動化配置

- [x] 3.1 建立 `.github/workflows/update_data.yml` 定時任務
- [x] 3.2 配置 Actions 權限：允許腳本寫入倉庫 (Write permission)
- [x] 3.3 設定 Git User 身分與自動 Commit/Push 流程

## 4. 前端靜態網頁 (GitHub Pages)

- [x] 4.1 撰寫 `web/index.html`：基礎佈局與 Tailwind CSS 引入
- [x] 4.2 實作數據加載邏輯：Fetch `index.json` 後加載最新日期的數據
- [x] 4.3 實作數據渲染表格與買賣顏色標示
- [x] 4.4 實作基礎搜尋功能：按代碼或內部人姓名進行即時篩選

## 5. 驗證與部署

- [x] 5.1 手動執行 Python 腳本，檢查 `data/` 下是否生成正確檔案
- [x] 5.2 測試 GitHub Actions 運行情況並檢查自動 Commit 是否成功
- [x] 5.3 開啟 GitHub Pages 設定，確認網站可正常訪問且加載數據
