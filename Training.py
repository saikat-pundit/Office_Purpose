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

def extract_name_from_page(text):
    pattern = r"Name of 1st Polling Officer\s*\n([^\n,]+(?:[,\s][^\n,]+)*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        # Clean possible trailing comma or extra spaces
        name = re.sub(r",\s*$", "", name)
        return name
    return None

def main():
    pdf_bytes = download_pdf(PDF_URL)
    names = []
    with pdfplumber.open(pdf_bytes) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                name = extract_name_from_page(text)
                if name:
                    names.append((page_num, name))
                else:
                    names.append((page_num, "NOT FOUND"))
            else:
                names.append((page_num, "NO TEXT"))

    # Print summary table
    print("\nSummary Table of 1st Polling Officers")
    print("=" * 60)
    print(f"{'Page':<6} {'1st Polling Officer Name':<50}")
    print("-" * 60)
    for page, name in names:
        print(f"{page:<6} {name:<50}")
    print("=" * 60)
    print(f"Total pages processed: {len(names)}")
    print(f"Names extracted: {sum(1 for _, n in names if n not in ('NOT FOUND','NO TEXT'))}")

if __name__ == "__main__":
    main()
