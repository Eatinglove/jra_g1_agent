import requests
from bs4 import BeautifulSoup
import os
import time

RACE_CODES = {
    "feb": "フェブラリーS",
    "takamatsu": "高松宮記念",
    "osaka": "大阪杯",
    "ouka": "桜花賞",
    "satsuki": "皐月賞",
    "haruten": "天皇賞（春）",
    "nmc": "NHKマイルC",
    "victoria": "ヴィクトリアマイル",
    "oaks": "オークス",
    "derby": "日本ダービー",
    "yasuda": "安田記念",
    "takara": "宝塚記念",
    "sprint": "スプリンターズS",
    "shuka": "秋華賞",
    "kikka": "菊花賞",
    "akiten": "天皇賞（秋）",
    "eliza": "エリザベス女王杯",
    "mile": "マイルCS",
    "jc": "ジャパンC",
    "jcd": "チャンピオンズC",
    "hjf": "阪神ジュベナイルF",
    "afs": "朝日杯FS",
    "hopeful": "ホープフルS",
    "arima": "有馬記念"
}

START_YEAR = 1970
END_YEAR = 2025
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def start_mega_scrape():

    folder_name = "race_data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    missing_data = []
    
    for code, jp_name in RACE_CODES.items():
        print(f"\n>>> 開始下載: {jp_name} ({code})")
        
        for year in range(START_YEAR, END_YEAR + 1):
            url = f"https://www.jra.go.jp/datafile/seiseki/g1/{code}/result/{code}{year}.html"
            file_path = f"{folder_name}/{code}_{year}.txt"
            
            try:

                time.sleep(0.2)
                
                response = requests.get(url, headers=HEADERS, timeout=10)
                
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    main_table = None
                    for table in soup.find_all('table'):
                        if "馬名" in table.get_text():
                            main_table = table
                            break
                    
                    if main_table:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(f"Source: {url}\n")
                            f.write(f"Race: {jp_name} {year}\n")
                            f.write("-" * 50 + "\n")
                            
                            rows = main_table.find_all('tr')
                            for row in rows:
                                cols = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                                f.write(" | ".join(cols) + "\n")
                        print(f"  [OK] {year}")
                    else:
                        missing_data.append(f"{year} {jp_name}: 網頁存在但找不到表格內容")
                else:
                    missing_data.append(f"{year} {jp_name}: HTTP {response.status_code} (可能該年尚未舉行)")

            except Exception as e:
                print(f"  [ERROR] {year} 出錯: {e}")
                missing_data.append(f"{year} {jp_name}: 程式異常 - {e}")

    with open("missing_data.txt", "w", encoding="utf-8") as f:
        f.write("=== JRA 歷史缺失資料報表 ===\n")
        f.write(f"掃描區間: {START_YEAR} - {END_YEAR}\n\n")
        for line in missing_data:
            f.write(line + "\n")
    
    print("\n" + "="*30)
    print("任務完成！資料夾: race_data")
    print("缺失詳情請見: missing_data.txt")

if __name__ == "__main__":
    start_mega_scrape()