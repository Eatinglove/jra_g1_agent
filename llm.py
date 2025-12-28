import requests
import json
import re
import os

API_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/generate"
API_KEY = "0a4bc6e85fb5a121e47c6b353f6f03764286b6e28a0476df3157062afa217d99"
MODEL = "gemma3:4b"
DB_FILE = "db.json"  

RACE_LIST_DESC = """
feb:二月錦標, takamatsu:高松宮記念, osaka:大阪杯, ouka:櫻花賞, satsuki:皐月賞, 
haruten:天皇賞春, nmc:NHK英里杯, victoria:維多利亞英里, oaks:奧克斯, derby:日本打比, 
yasuda:安田紀念, takara:寶塚紀念, sprint:短途馬錦標, shuka:秋華賞, kikka:菊花賞, 
akiten:天皇賞秋, eliza:伊莉莎白女王杯, mile:英里冠軍賽, jc:日本杯, jcd:冠軍杯(JCD), 
hjf:阪神JF, afs:朝日杯FS, hopeful:希望錦標, arima:有馬紀念
"""

class UltimateHorseRacingAgent:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db = {}
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
            print(f">>> 系統：成功載入 {len(self.db)} 場賽事數據。")
        else:
            print(f">>> 系統：找不到資料庫檔案 {db_path}")

    def call_api(self, prompt, is_json=False):
        headers = {"Authorization": f"Bearer {API_KEY}"}
        payload = {"model": MODEL, "prompt": prompt, "stream": False}
        if is_json:
            payload["format"] = "json"
        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=45)
            if response.status_code == 200:
                raw_text = response.json().get('response', '')
                if is_json:
                    match = re.search(r'\[.*\]|\{.*\}', raw_text, re.DOTALL)
                    return json.loads(match.group()) if match else []
                return raw_text
        except Exception as e:
            print(f"DEBUG: API 調用失敗 -> {e}")
        return None

    def start(self):
        #print("\n=== 全能賽馬數據分析師 Agent 啟動 ===")
        #print("支援功能：跨年份查詢、馬匹生涯冠軍追蹤、特定條件篩選。")
        
        while True:
            user_q = input("\n請輸入您的問題 (輸入 exit 離開): ").strip()
            if user_q.lower() in ['exit', 'quit']: break
            if not user_q: continue

            print("Agent 正在思考檢索策略...")
            plan_prompt = f"""
            你是一個賽馬資料庫分析師。資料標籤格式為 '賽事縮寫_年份'。
            可用的賽事縮寫：{RACE_LIST_DESC}
            
            任務：根據使用者的問題，決定需要從資料庫提取哪些標籤的數據。
            規則：
            1. 如果是查詢某馬匹的「生涯」或「哪些冠軍」，請只回傳 ["GLOBAL_SEARCH"]。
            2. 如果是查詢特定年份區間（如 2004-2006），請列出所有對應標籤。
            3. 如果是特定條件（如 2014年著差），請列出該年所有可能的 G1 標籤。
            4. 如果沒有特定規則則回傳最有可能符合使用者需求的標籤
            
            問題："{user_q}"
            請只回傳 JSON List 格式，例如: ["yasuda_2013", "takara_2004"]
            """
            
            keys_to_fetch = self.call_api(plan_prompt, is_json=True)
            if not keys_to_fetch:
                print("Agent：無法解析查詢計畫，請嘗試更具體的描述。")
                continue

            context = ""
            
            if "GLOBAL_SEARCH" in keys_to_fetch:
                print("正在執行全域搜索 (馬匹生涯追蹤)...")
                # 簡單提取可能的馬名 (中文或日文)
                horse_name = re.sub(r'[^\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff]', '', user_q.replace("生涯", "").replace("冠軍", ""))
                hits = []
                for k, v in self.db.items():
                    for row in v:
                        # 檢查馬名或記號 (處理位移) 且名次為 1
                        name_in_row = str(row.get("馬名", "")) + str(row.get("記号", ""))
                        if horse_name in name_in_row and row.get("着順") == "1":
                            hits.append({"賽事": k, "年份": k.split('_')[-1], "馬名": horse_name})
                context = f"全域搜索結果：馬匹 '{horse_name}' 的冠軍紀錄為：{json.dumps(hits, ensure_ascii=False)}"
            
            else:
                print(f"正在提取相關賽事數據：{keys_to_fetch}")
                for k in keys_to_fetch:
                    if k in self.db:
                        context += f"\n賽事 {k} 資料：\n" + json.dumps(self.db[k][:5], ensure_ascii=False)

            if not context:
                print("Agent：在資料庫中找不到相關數據。")
                continue

            print("Agent 正在整理數據並撰寫回答...")
            final_prompt = f"""
            你是一個專業賽馬分析師。請根據以下檢索到的精確數據回答問題。
            數據來源：{context}
            使用者問題："{user_q}"
            
            要求：
            1. 條列式回答，確保邏輯清晰。
            2. 對於身距(著差)、完賽時間、體重增減等細節要準確描述。
            3. 如果資料中有位移（如馬名跑進記號欄位），請聰明地辨識。
            4. 使用繁體中文。
            """
            
            answer = self.call_api(final_prompt)
            print("-" * 40)
            print(f"【分析結果】\n{answer if answer else 'API 回傳逾時，請縮短查詢範圍。'}")
            print("-" * 40)

if __name__ == "__main__":
    agent = UltimateHorseRacingAgent(DB_FILE)
    agent.start()