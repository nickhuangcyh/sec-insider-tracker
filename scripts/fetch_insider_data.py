import os
import json
from datetime import datetime, timedelta
from edgar import set_identity, get_filings

# SEC User-Agent Identity
set_identity("Nick Huang nickhuangcyh@gmail.com")

DATA_DIR = "data"
INDEX_FILE = os.path.join(DATA_DIR, "index.json")

def fetch_and_process():
    print("🚀 啟動 SEC Form 4 抓取器...")
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    try:
        print("正在從 SEC EDGAR 獲取最近的申報清單 (500 筆)...")
        filings = get_filings(form="4").head(500) 
    except Exception as e:
        print(f"❌ 獲取申報清單失敗: {e}")
        return
    
    target_dates = [
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    ]
    
    print(f"📅 目標日期: {target_dates}")
    
    for process_date in target_dates:
        date_filings = [f for f in filings if (f.filing_date if isinstance(f.filing_date, str) else f.filing_date.strftime("%Y-%m-%d")) == process_date]
        
        if not date_filings:
            print(f"💡 日期 {process_date} 沒有發現申報，跳過。")
            continue
            
        print(f"📂 正在搜尋 {process_date} 的交易資料 (最多嘗試 50 份)...")
        
        daily_data = {
            "date": process_date,
            "transactions": []
        }
        
        for filing in date_filings[:50]:
            try:
                f4 = filing.obj()
                if not f4 or not f4.non_derivative_table:
                    continue
                    
                found_in_filing = False
                for trans in f4.non_derivative_table.transactions:
                    if not trans or trans.transaction_code not in ['P', 'S']:
                        continue

                    owner = f4.reporting_owners[0]
                    daily_data["transactions"].append({
                        "ticker": f4.issuer.ticker if hasattr(f4.issuer, 'ticker') else "N/A",
                        "company": f4.issuer.name if hasattr(f4.issuer, 'name') else "N/A",
                        "insider": owner.name,
                        "title": owner.officer_title or owner.position or "N/A",
                        "date": trans.date,
                        "type": trans.transaction_code, 
                        "shares": int(trans.shares) if trans.shares is not None else 0,
                        "price": float(trans.price) if trans.price is not None else 0.0,
                        "value": float(trans.shares or 0) * float(trans.price or 0),
                        "url": filing.url
                    })
                    found_in_filing = True
                
                if found_in_filing and len(daily_data["transactions"]) >= 10:
                    print(f"  ✨ 已抓取到 {len(daily_data['transactions'])} 筆交易，提早結束。")
                    break
            except Exception:
                pass

        if daily_data["transactions"]:
            file_path = os.path.join(DATA_DIR, f"{process_date}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(daily_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 成功儲存 {process_date}.json (共 {len(daily_data['transactions'])} 筆交易)")
            update_index(process_date)
        else:
            print(f"⚠️ {process_date} 未發現符合條件的交易。")

def update_index(new_date):
    if not os.path.exists(INDEX_FILE):
        index = []
    else:
        try:
            with open(INDEX_FILE, "r") as f:
                index = json.load(f)
        except:
            index = []

    if new_date not in index:
        index.append(new_date)
    
    index = sorted(list(set(index)), reverse=True)

    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)
    print(f"📊 索引已更新 (index.json)")

if __name__ == "__main__":
    fetch_and_process()
