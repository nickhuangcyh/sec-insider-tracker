## ADDED Requirements

### Requirement: 按日期產出數據檔案
系統必須為每日抓取的交易數據生成獨立的 JSON 檔案，檔名格式為 `YYYY-MM-DD.json`。

#### Scenario: 成功生成今日檔案
- **WHEN** 數據抓取腳本完成解析
- **THEN** 系統應在 `data/` 目錄下建立一個以當日日期命名的 JSON 檔案，僅包含當日的交易數據

### Requirement: 維護數據索引 (Manifest)
系統必須維護一個 `data/index.json` 檔案，記錄目前所有可用的數據檔案日期列表。

#### Scenario: 更新索引檔案
- **WHEN** 新的日期檔案生成後
- **THEN** 系統應將新日期加入 `index.json` 的列表首位，並確保列表按日期倒序排列

### Requirement: 180 天檔案滾動清理 (File-based Retention)
系統必須僅保留最近 180 個日期的數據檔案，以控制倉庫大小。

#### Scenario: 自動刪除逾期檔案
- **WHEN** 索引檔案更新後，若日期總數超過 180
- **THEN** 系統應從 `index.json` 中移除最舊的日期，並刪除 `data/` 目錄下對應的舊 JSON 檔案
