import os
import sys
import json
import time
import signal
from datetime import datetime, timedelta
from edgar import set_identity, get_filings

set_identity("Nick Huang nickhuangcyh@gmail.com")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
INDEX_FILE = os.path.join(DATA_DIR, "index.json")
FAILED_FILE = os.path.join(DATA_DIR, "failed.json")
FILING_TIMEOUT_SECONDS = 5


class FilingTimeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise FilingTimeout()


signal.signal(signal.SIGALRM, _timeout_handler)


def parse_args():
    """無參數時預設抓昨天，--retry 重試失敗的，有參數時抓指定日期範圍。"""
    if len(sys.argv) == 2 and sys.argv[1] == "--retry":
        return None, None  # retry mode
    elif len(sys.argv) == 3:
        return sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 1:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return yesterday, yesterday
    else:
        print("用法: python3 fetch_insider_data.py [start_date end_date]")
        print("      python3 fetch_insider_data.py --retry")
        print("  例: python3 fetch_insider_data.py 2026-05-01 2026-05-18")
        print("  無參數時預設抓昨天的資料")
        print("  --retry 重新抓取之前失敗的 filing")
        sys.exit(1)


def get_existing_dates():
    """讀取 index.json，回傳已存在的日期 set。"""
    if not os.path.exists(INDEX_FILE):
        return set()
    try:
        with open(INDEX_FILE, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()


def update_index(dates_to_add):
    """將新日期加入 index.json。"""
    existing = get_existing_dates()
    merged = sorted(existing | set(dates_to_add), reverse=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(merged, f, indent=2)
    print(f"📊 索引已更新，共 {len(merged)} 個日期", flush=True)


def load_failed():
    if not os.path.exists(FAILED_FILE):
        return {}
    try:
        with open(FAILED_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_failed(failed):
    """儲存失敗紀錄，格式: {date: [{accession, url, reason}]}"""
    if failed:
        with open(FAILED_FILE, "w") as f:
            json.dump(failed, f, indent=2, ensure_ascii=False)
    elif os.path.exists(FAILED_FILE):
        os.remove(FAILED_FILE)


TRANSACTION_NAMES = {
    'P': 'Purchase', 'S': 'Sale', 'A': 'Grant',
    'M': 'Exercise', 'X': 'Exercise', 'F': 'Tax Withholding',
    'G': 'Gift', 'D': 'Disposition', 'C': 'Conversion',
}

TRACKED_CODES = set(TRANSACTION_NAMES.keys())


def process_filing(filing, accession):
    """解析單一 filing，成功回傳 transactions list，失敗 raise exception。"""
    signal.alarm(FILING_TIMEOUT_SECONDS)
    f4 = filing.obj()
    if not f4 or not f4.non_derivative_table:
        signal.alarm(0)
        return []

    table = f4.non_derivative_table
    if not table.has_transactions:
        signal.alarm(0)
        return []

    owner = f4.reporting_owners[0]
    ticker = getattr(f4.issuer, 'ticker', 'N/A')
    company = getattr(f4.issuer, 'name', 'N/A')

    results = []
    df = table.transactions.data
    for idx, row in df.iterrows():
        code = row.get('Code', '')
        if code not in TRACKED_CODES:
            continue
        shares_raw = row.get('Shares')
        price_raw = row.get('Price')
        remaining_raw = row.get('Remaining')
        shares = int(shares_raw) if shares_raw is not None and shares_raw == shares_raw else 0
        price = float(price_raw) if price_raw is not None and price_raw == price_raw else 0.0
        remaining = int(remaining_raw) if remaining_raw is not None and remaining_raw == remaining_raw else None
        results.append({
            "ticker": ticker,
            "company": company,
            "insider": owner.name,
            "relationship": owner.position or "N/A",
            "title": owner.officer_title or owner.position or "N/A",
            "date": row.get('Date', ''),
            "type": code,
            "transaction": TRANSACTION_NAMES.get(code, code),
            "shares": shares,
            "price": price,
            "value": shares * price,
            "shares_total": remaining,
            "url": filing.url
        })
    signal.alarm(0)
    return results


def fetch_and_process(start_date, end_date):
    os.makedirs(DATA_DIR, exist_ok=True)

    existing_dates = get_existing_dates()
    print(f"🚀 抓取範圍: {start_date} ~ {end_date}", flush=True)
    print(f"📁 已有 {len(existing_dates)} 個日期的資料", flush=True)

    print(f"正在從 SEC EDGAR 獲取 Form 4 申報清單...", flush=True)
    t0 = time.time()
    try:
        filings = get_filings(form="4", filing_date=f"{start_date}:{end_date}")
        print(f"✅ 取得申報清單完成，耗時 {time.time() - t0:.1f}s，共 {len(filings)} 筆", flush=True)
    except Exception as e:
        print(f"❌ 獲取申報清單失敗: {e}", flush=True)
        return

    # 按日期分組
    date_groups = {}
    for filing in filings:
        d = filing.filing_date if isinstance(filing.filing_date, str) else filing.filing_date.strftime("%Y-%m-%d")
        if d not in date_groups:
            date_groups[d] = []
        date_groups[d].append(filing)

    failed = load_failed()
    new_dates = []
    for process_date in sorted(date_groups.keys()):
        if process_date in existing_dates:
            print(f"⏭️  {process_date} 已存在，跳過", flush=True)
            continue

        date_filings = date_groups[process_date]
        print(f"\n📂 處理 {process_date} (共 {len(date_filings)} 份申報)...", flush=True)

        transactions = []
        seen_accessions = set()
        date_failed = []

        for idx, filing in enumerate(date_filings, start=1):
            accession = getattr(filing, 'accession_no', 'N/A')
            if accession in seen_accessions:
                print(f"  [{idx}/{len(date_filings)}] {accession} 重複，跳過", flush=True)
                continue
            seen_accessions.add(accession)
            print(f"  [{idx}/{len(date_filings)}] {accession}", end="", flush=True)

            t_start = time.time()
            try:
                results = process_filing(filing, accession)
                elapsed = time.time() - t_start
                if results:
                    transactions.extend(results)
                    print(f" {elapsed:.1f}s +{len(results)}tx", flush=True)
                else:
                    print(f" {elapsed:.1f}s skip", flush=True)

            except FilingTimeout:
                signal.alarm(0)
                elapsed = time.time() - t_start
                print(f" ⏰ 超時({elapsed:.0f}s)", flush=True)
                date_failed.append({"accession": accession, "url": getattr(filing, 'url', ''), "reason": "timeout"})
            except Exception as e:
                signal.alarm(0)
                elapsed = time.time() - t_start
                print(f" ❌ {elapsed:.1f}s {type(e).__name__}: {e}", flush=True)
                date_failed.append({"accession": accession, "url": getattr(filing, 'url', ''), "reason": f"{type(e).__name__}: {e}"})

        if transactions:
            file_path = os.path.join(DATA_DIR, f"{process_date}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({"date": process_date, "transactions": transactions}, f, indent=2, ensure_ascii=False)
            print(f"  ✅ 儲存 {process_date}.json ({len(transactions)} 筆交易)", flush=True)
            new_dates.append(process_date)
        else:
            print(f"  ⚠️ {process_date} 無符合條件的交易", flush=True)

        # 更新失敗紀錄
        if date_failed:
            failed[process_date] = date_failed
        elif process_date in failed:
            del failed[process_date]

    save_failed(failed)
    if new_dates:
        update_index(new_dates)

    total_failed = sum(len(v) for v in failed.values())
    print(f"\n🏁 完成！新增 {len(new_dates)} 個日期的資料", flush=True)
    if total_failed:
        print(f"⚠️  共 {total_failed} 筆失敗紀錄已存入 data/failed.json，可用 --retry 重試", flush=True)


def retry_failed():
    """重試 failed.json 中記錄的失敗 filing。"""
    failed = load_failed()
    if not failed:
        print("✅ 沒有需要重試的失敗紀錄", flush=True)
        return

    print(f"🔄 重試失敗的 filing (共 {sum(len(v) for v in failed.values())} 筆)...", flush=True)

    remaining_failed = {}
    for process_date, items in sorted(failed.items()):
        print(f"\n📂 重試 {process_date} ({len(items)} 筆)...", flush=True)

        # 載入該日期已有的資料
        file_path = os.path.join(DATA_DIR, f"{process_date}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                existing_data = json.load(f)
            transactions = existing_data.get("transactions", [])
        else:
            transactions = []

        date_still_failed = []
        # 需要重新取得 filings 來 retry
        print(f"  正在取得 {process_date} 的申報清單...", flush=True)
        try:
            filings = get_filings(form="4", filing_date=f"{process_date}:{process_date}")
        except Exception as e:
            print(f"  ❌ 無法取得申報清單: {e}", flush=True)
            remaining_failed[process_date] = items
            continue

        # 建立 accession -> filing 的對照
        filing_map = {}
        for filing in filings:
            acc = getattr(filing, 'accession_no', None)
            if acc and acc not in filing_map:
                filing_map[acc] = filing

        for item in items:
            accession = item["accession"]
            filing = filing_map.get(accession)
            if not filing:
                print(f"  [{accession}] 找不到 filing，跳過", flush=True)
                continue

            print(f"  [{accession}]", end="", flush=True)
            t_start = time.time()
            try:
                results = process_filing(filing, accession)
                elapsed = time.time() - t_start
                if results:
                    transactions.extend(results)
                    print(f" ✅ {elapsed:.1f}s +{len(results)}tx", flush=True)
                else:
                    print(f" {elapsed:.1f}s skip (no P/S)", flush=True)
            except FilingTimeout:
                signal.alarm(0)
                print(f" ⏰ 仍然超時", flush=True)
                date_still_failed.append(item)
            except Exception as e:
                signal.alarm(0)
                print(f" ❌ {type(e).__name__}: {e}", flush=True)
                date_still_failed.append({**item, "reason": f"{type(e).__name__}: {e}"})

        if transactions:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({"date": process_date, "transactions": transactions}, f, indent=2, ensure_ascii=False)
            print(f"  ✅ 更新 {process_date}.json ({len(transactions)} 筆交易)", flush=True)
            # 確保在 index 裡
            update_index([process_date])

        if date_still_failed:
            remaining_failed[process_date] = date_still_failed

    save_failed(remaining_failed)
    still_count = sum(len(v) for v in remaining_failed.values())
    if still_count:
        print(f"\n⚠️  仍有 {still_count} 筆失敗", flush=True)
    else:
        print(f"\n✅ 所有重試都成功！", flush=True)


if __name__ == "__main__":
    start_date, end_date = parse_args()
    if start_date is None:
        retry_failed()
    else:
        fetch_and_process(start_date, end_date)
