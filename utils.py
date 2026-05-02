import os
import pandas as pd
import json
import tempfile
import shutil

# =============================
# OCR

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
        "path": "district/ontime/อำเภอเมืองบุรีรัมย์/ตำบลถลุงเหล็ก",
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
    {
        "path": "referendum/outside/อส 4-7 นอกเขตออกเสียง",
        "pages": 4
    },
    {
        "path": "referendum/inside/อำเภอบ้านด่าน/ตำบลบ้านด่าน",
        "pages": 40
    },
    {
        "path": "referendum/inside/อำเภอบ้านด่าน/ตำบลปราสาท",
        "pages": 32
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลกระสัง",
        "pages": 28
    },
    {
        "path": "referendum/inside/อำเภอเมืองบุรีรัมย์/ตำบลกลันทา",
        "pages": 26
    },
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

OCR_STEPS = {"district": 2, "partylist": 4, "referendum": 2}

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

# ดึงข้อมูล file ocr
def load_ocr_data(file_name: str, page_num: int):
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

OCR_OUTPUT_CLEAN_DIR = os.path.join(BASE_DIR, "ocr_output_clean")

# ดึงข้อมูล file ocr ที่ clean แล้ว
def load_ocr_clean_data(file_name: str, page_num: int):
    key = f"{file_name}_{page_num}"
    
    base_name = os.path.basename(file_name)
    dir_name = os.path.dirname(file_name).replace(".pdf", "")
    
    output_path = os.path.join(OCR_OUTPUT_CLEAN_DIR, dir_name, f"{base_name}_{page_num}.json")
    
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
       
# =============================
# Process

def validate_district(summary: dict, df: pd.DataFrame, file_path: str) -> list[dict]:
    issues = []
    total = summary.get("จำนวนบัตรทั้งหมด", 0)
    good = summary.get("บัตรดี", 0)
    bad = summary.get("บัตรเสีย", 0)
    none = summary.get("ไม่เลือกผู้ใด", 0)
    score_sum = df["คะแนน"].sum() if not df.empty else 0

    if total < 0 or good < 0 or bad < 0 or none < 0:
        issues.append({"file": file_path, "type": "district", "issue": f"มีค่าติดลบ total={total} good={good} bad={bad} none={none}"})
    if total == 0:
        issues.append({"file": file_path, "type": "district", "issue": "จำนวนบัตรทั้งหมด = 0"})
    if good == 0:
        issues.append({"file": file_path, "type": "district", "issue": "บัตรดี = 0"})
    if good + bad + none > total:
        issues.append({"file": file_path, "type": "district", "issue": f"บัตรดี({good}) + บัตรเสีย({bad}) + ไม่เลือกผู้ใด({none}) = {good+bad+none} > จำนวนบัตรทั้งหมด({total})"})
    if not df.empty and score_sum != good:
        issues.append({"file": file_path, "type": "district", "issue": f"sum คะแนนผู้สมัคร({score_sum}) ≠ บัตรดี({good})"})

    return issues

def validate_partylist(summary: dict, df: pd.DataFrame, file_path: str) -> list[dict]:
    issues = []
    total = summary.get("จำนวนบัตรทั้งหมด", 0)
    good = summary.get("บัตรดี", 0)
    bad = summary.get("บัตรเสีย", 0)
    none = summary.get("ไม่เลือกผู้ใด", 0)
    score_sum = df["คะแนน"].sum() if not df.empty else 0

    if total < 0 or good < 0 or bad < 0 or none < 0:
        issues.append({"file": file_path, "type": "partylist", "issue": f"มีค่าติดลบ total={total} good={good} bad={bad} none={none}"})
    if total == 0:
        issues.append({"file": file_path, "type": "partylist", "issue": "จำนวนบัตรทั้งหมด = 0"})
    if good == 0:
        issues.append({"file": file_path, "type": "partylist", "issue": "บัตรดี = 0"})
    if good + bad + none > total:
        issues.append({"file": file_path, "type": "partylist", "issue": f"บัตรดี({good}) + บัตรเสีย({bad}) + ไม่เลือกผู้ใด({none}) = {good+bad+none} > จำนวนบัตรทั้งหมด({total})"})
    if not df.empty and score_sum != good:
        issues.append({"file": file_path, "type": "partylist", "issue": f"sum คะแนนพรรค({score_sum}) != บัตรดี({good})"})

    return issues

def validate_referendum(summary: dict, df: pd.DataFrame, file_path: str) -> list[dict]:
    issues = []
    eligible = summary.get("ผู้มีสิทธิ", 0)
    voted = summary.get("ผู้มาใช้สิทธิ", 0)
    bad_voted = summary.get("บัตรเสีย", 0)
    score_sum = df["คะแนน"].sum() if not df.empty else 0

    if eligible < 0 or voted < 0 or bad_voted < 0:
        issues.append({"file": file_path, "type": "referendum", "issue": f"มีค่าติดลบ eligible={eligible} voted={voted} bad_voted={bad_voted}"})
    if eligible == 0:
        issues.append({"file": file_path, "type": "referendum", "issue": "ผู้มีสิทธิ = 0"})
    if voted == 0:
        issues.append({"file": file_path, "type": "referendum", "issue": "มาใช้สิทธิ = 0"})
    if voted > eligible:
        issues.append({"file": file_path, "type": "referendum", "issue": f"มาใช้สิทธิ({voted}) > ผู้มีสิทธิ({eligible})"})
    if bad_voted > voted:
        issues.append({"file": file_path, "type": "referendum", "issue": f"บัตรเสีย({bad_voted}) > มาใช้สิทธิ({voted})"})
    if score_sum != voted - bad_voted:
        issues.append({"file": file_path, "type": "referendum", "issue": f"sum คะแนน({score_sum}) != มาใช้สิทธิ({voted}) - ทำบัตรเสีย({bad_voted})"})

    return issues

def run_validation() -> pd.DataFrame:
    all_issues = []

    for file_config in OCR_FILES:
        path = file_config["path"]
        pages = file_config["pages"]
        file_type = path.split("/")[0]
        step = OCR_STEPS.get(file_type, 1)

        for page_num in range(1, pages, step):
            file_label = f"{path}_{page_num}"
            result = load_ocr_clean_data(path, page_num)
            summary = result[f"{path}_{page_num}"]["summary"]
            df = result[f"{path}_{page_num}"]["df"]

            if file_type == "district":
                all_issues.extend(validate_district(summary, df, file_label))
            elif file_type == "partylist":
                all_issues.extend(validate_partylist(summary, df, file_label))
            elif file_type == "referendum":
                all_issues.extend(validate_referendum(summary, df, file_label))

    df_issues = pd.DataFrame(all_issues)

    print(f"Issues: {len(df_issues)} row(s)")
    print(f' - District Issues: {len(df_issues[df_issues["type"] == "district"])}')
    print(f' - Partylist Issues: {len(df_issues[df_issues["type"] == "partylist"])}')
    print(f' - Referendum Issues: {len(df_issues[df_issues["type"] == "referendum"])}')
    
    df_issues.to_csv("02_validation_issues.csv", index=False, encoding="utf-8-sig")

    return df_issues

def parse_path_meta(key: str):
    parts = key.split("/")
    amphoe = next((p for p in parts if p.startswith("อำเภอ")), "นอกเขต")
    tambon = next((p for p in parts if p.startswith("ตำบล")), "นอกเขต")
    return amphoe, tambon

def flatten_district(dfs_list):
    rows_scores = []
    rows_summary = []
    for d in dfs_list:
        for key, val in d.items():
            amphoe, tambon = parse_path_meta(key)
            summary = val["summary"]
            df = val["df"]
            if "_" in tambon:
                tambon, unit = tambon.split("_")
                unit = str(int(unit) // OCR_STEPS["district"] + 1)
            else :
                tambon = tambon
                unit = "ไม่ทราบ"
            meta = {"unit_key": key, "อำเภอ": amphoe, "ตำบล": tambon, "หน่วย": unit}
            rows_summary.append({**meta, **summary})
            if not df.empty:
                for _, row in df.iterrows():
                    rows_scores.append({**meta, **row.to_dict()})
    return pd.DataFrame(rows_summary), pd.DataFrame(rows_scores)

def flatten_partylist(dfs_list):
    rows_scores = []
    rows_summary = []
    for d in dfs_list:
        for key, val in d.items():
            amphoe, tambon = parse_path_meta(key)
            summary = val["summary"]
            df = val["df"]
            if "_" in tambon:
                tambon, unit = tambon.split("_")
                unit = str(int(unit) // OCR_STEPS["partylist"] + 1)
            else :
                tambon = tambon
                unit = "ไม่ทราบ"
            meta = {"unit_key": key, "อำเภอ": amphoe, "ตำบล": tambon, "หน่วย": unit}
            rows_summary.append({**meta, **summary})
            if not df.empty:
                for _, row in df.iterrows():
                    rows_scores.append({**meta, **row.to_dict()})
    return pd.DataFrame(rows_summary), pd.DataFrame(rows_scores)

def flatten_referendum(dfs_list):
    rows_scores = []
    rows_summary = []
    for d in dfs_list:
        for key, val in d.items():
            amphoe, tambon = parse_path_meta(key)
            summary = val["summary"]
            df = val["df"]
            if "_" in tambon:
                tambon, unit = tambon.split("_")
                unit = str(int(unit) // 2 + 1)
            else :
                tambon = tambon
                unit = "ไม่ทราบ"
            meta = {"unit_key": key, "อำเภอ": amphoe, "ตำบล": tambon, "หน่วย": unit}
            rows_summary.append({**meta, **summary})
            if not df.empty:
                for _, row in df.iterrows():
                    rows_scores.append({**meta, **row.to_dict()})
    return pd.DataFrame(rows_summary), pd.DataFrame(rows_scores)