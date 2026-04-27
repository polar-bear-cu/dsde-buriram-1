import os
import pandas as pd
import json

OCR_OUTPUT_DIR = "ocr_output"

# เก็บผลลัพธ์การ ocr
def save_ocr_output(file_name: str, page_num: int, summary: dict, df: pd.DataFrame):
    base_name = os.path.basename(file_name)
    dir_name = os.path.dirname(file_name).replace('data/', '').replace(".pdf", "")
    
    os.makedirs(OCR_OUTPUT_DIR, exist_ok=True)
    os.makedirs(f"{OCR_OUTPUT_DIR}/{dir_name}", exist_ok=True)
    
    result = {
        "summary": summary,
        "data": df.to_dict(orient="records") if df is not None else []
    }
    
    with open(f"{OCR_OUTPUT_DIR}/{dir_name}/{base_name}_{page_num}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

# แปลงเลขไทยเป็นเลขอารบิก
def thai_to_arabic(text):
    thai_digits = '๐๑๒๓๔๕๖๗๘๙'
    arabic_digits = '0123456789'
    trans = str.maketrans(thai_digits, arabic_digits)
    return text.translate(trans)

# แปลงข้อความเป็นเลข     
def parse_number(val):
    val = str(val)
    if not val:
        return None
    val = val.replace(',', '').strip()
    if val == '-' or val == '':
        return 0
    return int(val)

# ถ้าค่าใน column พรรค เป็นตัวเลข ให้เอามาใส่แทนที่ใน column คะแนน
def swap_if_party_is_numeric(row):
    party_val = str(row['พรรค']).strip()
    if party_val.isdigit():
        return pd.Series({'พรรค': row['คะแนน'], 'คะแนน': party_val})
    return row

# ดึงข้อมูล file
def load_data(file_name: str, page_num: int):
    key = f"{file_name}_{page_num}"
    
    with open(f'ocr_output/{file_name}_{page_num}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    summary = data.get("summary", {})
    df = pd.DataFrame(data.get("data", []))
    
    return {
        key: {
            "df": df,
            "summary": summary
        }
    }