## ADDED Requirements

### Requirement: 獲取最新 Form 4 申報
系統必須能夠透過 `edgartools` 或直接 API 調用，從 SEC EDGAR 系統獲取最新的 Form 4 (Statement of Changes in Beneficial Ownership) 申報列表。

#### Scenario: 成功獲取近期申報
- **WHEN** 執行數據抓取腳本並指定獲取數量（例如最近 100 筆）
- **THEN** 系統應返回一個包含最新申報物件的列表，且每個物件都應包含有效的訪問編號 (Accession Number)

### Requirement: 解析交易數據
系統必須能夠從 Form 4 的 XML 內容中解析出「非衍生性交易 (Non-Derivative Transactions)」（即普通的股票買賣）。

#### Scenario: 提取關鍵交易欄位
- **WHEN** 解析一個包含股票買賣的 Form 4 XML 文件
- **THEN** 系統必須提取以下欄位：代碼 (Ticker)、公司名稱 (Issuer)、內部人姓名 (Reporting Owner)、職位 (Title)、交易日期 (Date)、交易代碼 (P=買, S=賣)、股數 (Shares)、成交價格 (Price) 以及交易後的持股數 (Owned After)

### Requirement: 符合 SEC User-Agent 規範
系統在與 SEC EDGAR 進行通訊時，必須在 HTTP Header 中包含符合規範的 User-Agent 標識。

#### Scenario: 設定身分標識
- **WHEN** 發起 API 請求到 `sec.gov`
- **THEN** 請求 Header 必須包含格式為 `"Name Email"` 的標識，以符合 SEC 的存取原則
