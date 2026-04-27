import os
import pandas as pd
import json
import tempfile
import shutil

OCR_OUTPUT_DIR = "ocr_output"
OCR_FILES = [
    # ================ DISTRICT ==================
    {
        "path": "district/advance/5-17 เขต 1 จ.บุรีรัมย์", 
        "pages": 16
    },
    {
        "path": "district/ontime/อำเภอบ้านด่าน/ตำบลบ้านด่าน",
        "pages": 40
    },
    {
        "path": "district/ontime/อำเภอบ้านด่าน/ตำบลปราสาท",
        "pages": 32
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/5ทับ18 ตำบลถลุงเหล็ก",
        "pages": 28
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลกระสัง",
        "pages": 28
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลกลันทา",
        "pages": 26
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลชุมเห็ด",
        "pages": 64
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลในเมือง",
        "pages": 62
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลบัวทอง",
        "pages": 28
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลบ้านบัว",
        "pages": 38
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลบ้านยาง",
        "pages": 44
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลพระครู",
        "pages": 22
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลลุมปุ๊ก",
        "pages": 38,
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลสะแกโพรง",
        "pages": 48,
    },
    {
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลหนองตาด",
        "pages": 44
    },
    
    # ================ PARTYLIST ==================
    {
        "path": "partylist/advance/5-17(บช)",
        "pages": 32,
    },
    {
        "path": "partylist/ontime/อำเภอบ้านด่าน/ตำบลบ้านด่าน",
        "pages": 80
    },
    {
        "path": "partylist/ontime/อำเภอบ้านด่าน/ตำบลปราสาท",
        "pages": 64
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลกระสัง",
        "pages": 56
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลกลันทา",
        "pages": 52
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลชุมเห็ด",
        "pages": 128
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลถลุงเหล็ก",
        "pages": 56
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลในเมือง",
        "pages": 124
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลบัวทอง",
        "pages": 56
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลบ้านบัว",
        "pages": 76
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลบ้านยาง",
        "pages": 88
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลพระครู",
        "pages": 44
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลลุมปุ๊ก",
        "pages": 76
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลสะแกโพรง",
        "pages": 96
    },
    {
        "path": "partylist/ontime/อำเภอเมืองบุรีรัมย์/ตำบลหนองตาด",
        "pages": 88
    },
    
    # ================ REFERENDUM ==================
    # {
    #     "path": "referendum/outside/อส 4-7 นอกเขตออกเสียง",
    #     "pages": 4
    # },
    # {
    #     "path": "referendum/inside/อำเภอบ้านด่าน/ตำบลบ้านด่าน",
    #     "pages": 40
    # },
    # {
    #     "path": "referendum/inside/อำเภอบ้านด่าน/ตำบลปราสาท",
    #     "pages": 32
    # },
    # {
    #     "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลกระสัง",
    #     "pages": 28
    # },
    # {
    #     "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลกลันทา",
    #     "pages": 26
    # },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลชุมเห็ด",
        "pages": 62
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลถลุงเหล็ก",
        "pages": 28
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลในเมือง",
        "pages": 62
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลบัวทอง",
        "pages": 28
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลบ้านบัว",
        "pages": 38
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลบ้านยาง",
        "pages": 44
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลพระครู",
        "pages": 22
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลลุมปุ๊ก",
        "pages": 38
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลสะแกโพรง",
        "pages": 48
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลหนองตาด",
        "pages": 44
    },
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_safe_pdf_path(file_name):
    src = os.path.join(BASE_DIR, "data", f"{file_name}.pdf")
    
    if not os.path.exists(src):
        raise FileNotFoundError(src)

    tmp_dir = tempfile.mkdtemp()
    safe_path = os.path.join(tmp_dir, "file.pdf")
    
    shutil.copy(src, safe_path)
    return safe_path

# เก็บผลลัพธ์การ ocr
OCR_OUTPUT_DIR = os.path.join(BASE_DIR, "ocr_output")

def save_ocr_output(file_name: str, page_num: int, summary: dict, df: pd.DataFrame):
    base_name = os.path.basename(file_name)
    dir_name = os.path.dirname(file_name).replace(".pdf", "")
    
    output_dir = os.path.join(OCR_OUTPUT_DIR, dir_name)
    os.makedirs(output_dir, exist_ok=True)
    
    result = {
        "name": f"{file_name}_{page_num}",
        "summary": summary,
        "data": df.to_dict(orient="records") if df is not None else []
    }
    
    output_path = os.path.join(output_dir, f"{base_name}_{page_num}.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
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
    
    base_name = os.path.basename(file_name)
    dir_name = os.path.dirname(file_name).replace(".pdf", "")
    
    output_path = os.path.join(OCR_OUTPUT_DIR, dir_name, f"{base_name}_{page_num}.json")
    
    with open(output_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    summary = data.get("summary", {})
    df = pd.DataFrame(data.get("data", []))
    
    return {
        key: {
            "df": df,
            "summary": summary
        }
    }