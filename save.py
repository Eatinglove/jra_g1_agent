import json
import os
import re

def is_weight_diff(text):
    clean = text.strip('() ')
    return bool(re.match(r'^[+-]\d+$', clean) or clean == "0" or clean == "前計不")

def is_time_format(text):
    return ":" in text and any(c.isdigit() for c in text)

def is_rank_num(text):

    clean = text.replace('<b>','').replace('</b>','').strip()
    return clean.isdigit() and 1 <= int(clean) <= 30

def final_safe_parser(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    filename = os.path.basename(file_path)
    year_match = re.search(r'\d{4}', filename)
    year = int(year_match.group()) if year_match else 2025
    
    results = []
    header_list = []

    for line in lines:
        line = line.strip()
        if "|" not in line: continue
        
        raw_parts = [p.strip() for p in line.split('|')]
        if not raw_parts: continue
        if raw_parts[0] == "": raw_parts = raw_parts[1:]
        if raw_parts and raw_parts[-1] == "": raw_parts = raw_parts[:-1]
        
        if not raw_parts: continue

        if "着順" in line and "馬名" in line and not is_rank_num(raw_parts[0]):
            header_list = [h for h in raw_parts if h]
            if year >= 2006 and "枠" in header_list:
                header_list.remove("枠")
            continue

        if header_list and is_rank_num(raw_parts[0]):
            rank = raw_parts[0].replace('<b>','').replace('</b>','')

            working_parts = raw_parts[:]
            if year >= 2006 and len(working_parts) > 1:
                working_parts.pop(1)

            cleaned_row = []
            skip = False
            for i in range(len(working_parts)):
                if skip:
                    skip = False
                    continue
                
                curr = working_parts[i]
                
                if i + 1 < len(working_parts):
                    nxt = working_parts[i+1]
                    if any(c.isdigit() for c in curr) and is_weight_diff(nxt) and not is_time_format(curr):
                        cleaned_row.append(f"{curr}({nxt.strip('()')})")
                        skip = True
                        continue
                
                if curr == "" and i + 1 < len(working_parts):
                    nxt = working_parts[i+1]
                    if nxt != "" and not any(c.isdigit() for c in nxt):
                        continue

                cleaned_row.append(curr)

            entry = {}
            data_ptr = 0
            for head in header_list:
                if data_ptr >= len(cleaned_row):
                    entry[head] = "" 
                    continue
                
                if head == "着差" and rank == "1":
                    ptr_val = cleaned_row[data_ptr]
                    if is_time_format(ptr_val) or (any(c.isdigit() for c in ptr_val) and ("Kg" in ptr_val or "(" in ptr_val)):
                        entry[head] = ""
                        continue
                
                entry[head] = cleaned_row[data_ptr]
                data_ptr += 1
                
            if entry:
                results.append(entry)
            
    return results

def main():
    input_folder = "race_data"
    output_file = "db.json"
    master_db = {}
    
    if not os.path.exists(input_folder):
        print(f"錯誤：找不到資料夾 '{input_folder}'")
        return

    files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]
    print(f"正在分析 {len(files)} 個檔案...")

    for filename in files:
        try:
            res = final_safe_parser(os.path.join(input_folder, filename))
            if res:
                master_db[filename.replace(".txt", "")] = res
                print(f"  [✓] {filename}")
        except Exception as e:
            print(f"  [✗] {filename} 發生錯誤: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(master_db, f, ensure_ascii=False, indent=4)
    
    print("\n" + "="*30)
    print(f"轉換完成！知識庫已存至: {output_file}")
    print("="*30)
    input("\n程式執行完畢，請按 Enter 鍵結束...")

if __name__ == "__main__":
    main()