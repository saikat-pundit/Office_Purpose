import re
import sys
from pathlib import Path
import pdfplumber
import pandas as pd

def extract_name_and_details(page_text):
    name_pattern = r"Name of 1st Polling Officer\s*\n*(.*?)(?:\n|$)"
    match = re.search(name_pattern, page_text, re.IGNORECASE)
    if not match:
        return None, None, None
    name_line = match.group(1).strip()
    name_clean = re.sub(r",\s*MOBILE NO:.*$", "", name_line).strip()

    mobile_match = re.search(r"MOBILE NO:\s*(\d+)", page_text)
    epic_match = re.search(r"EPIC No\.\s*-\s*([A-Z0-9]+)", page_text)
    mobile = mobile_match.group(1) if mobile_match else None
    epic = epic_match.group(1) if epic_match else None
    return name_clean, mobile, epic

def main(pdf_path, output_csv):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            name, mobile, epic = extract_name_and_details(text)
            data.append({
                "Page": page_num,
                "1st_Polling_Officer": name,
                "Mobile": mobile,
                "EPIC": epic
            })
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"Extracted {len(df)} records to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_polling_officers.py <pdf_file> <output_csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
