# extract_polling_officers.py
import re
import sys
import requests
from io import BytesIO
import pdfplumber

PDF_URL = "https://drive.google.com/uc?export=download&id=1rd5eRjpcnYwfJUSfq84Rtl2M6R4Pw70Q"

def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)

def extract_name_only(text):
    """
    Extract just the name part before the first comma after 'Name of 1st Polling Officer'.
    """
    pattern = r"Name of 1st Polling Officer\s*\n([^\n,]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        return name
    return None

def main():
    pdf_bytes = download_pdf(PDF_URL)
    names = []
    with pdfplumber.open(pdf_bytes) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                name = extract_name_only(text)
                if name:
                    names.append((page_num, name))
                else:
                    names.append((page_num, "NOT FOUND"))
            else:
                names.append((page_num, "NO TEXT"))

    # Print summary table
    print("\nSummary Table of 1st Polling Officers")
    print("=" * 55)
    print(f"{'Page':<6} {'1st Polling Officer Name':<30} {'Role':<15}")
    print("-" * 55)
    for page, name in names:
        role = "1st Polling Officer" if name != "NOT FOUND" and name != "NO TEXT" else ""
        print(f"{page:<6} {name:<30} {role:<15}")
    print("=" * 55)
    print(f"Total pages processed: {len(names)}")
    print(f"Names extracted: {sum(1 for _, n in names if n not in ('NOT FOUND','NO TEXT'))}")

if __name__ == "__main__":
    main()
