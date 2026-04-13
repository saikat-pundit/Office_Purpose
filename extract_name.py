import re
import gdown
import PyPDF2
import os

def extract_name_from_pdf():
    # Google Drive file ID from your link
    file_id = '1vneN2mHfbCrvh738i7_QXNC0vz5-hXXa'
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'appointment_letter.pdf'
    
    print("Downloading PDF from Google Drive...")
    gdown.download(url, output, quiet=False)
    
    ticked_names = []
    reserve_names = []
    
    # Regex pattern to find the exact role string
    role_pattern = r'((?:1st|2nd|3rd|4th)?\s*(?:Polling|Presiding)\s*Officer)'
    
    try:
        # Read the downloaded PDF
        with open(output, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Loop through ALL pages in the PDF
            for page in reader.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # 1. Check for Reserve (RSV) names
                rsv_matches = re.finditer(r'RSV[\W_]*?([A-Z\s]{4,}?)(?=[,\n]|ASSISTANT)', text, re.IGNORECASE)
                for match in rsv_matches:
                    name = match.group(1).strip()
                    # Search for the role in the next 150 characters to avoid crossing into the next person
                    start_idx = match.end()
                    search_area = text[start_idx:start_idx+150]
                    role_match = re.search(role_pattern, search_area, re.IGNORECASE)
                    
                    if role_match:
                        role = role_match.group(1).strip(" ()").title()
                        reserve_names.append(f"{name} ({role})")
                    else:
                        reserve_names.append(name)
                
                # 2. Regex for Ticked names (Pattern: √ 1. NAME)
                matches_t1 = re.finditer(r'√[\s\n]*\d+\.[\s\n]*([A-Z\s]+?)(?=[,\n]|ASSISTANT|PRIMARY|LIBRARIAN|OFFICE|HEAD TEACHER)', text, re.IGNORECASE)
                for match in matches_t1:
                    name = match.group(1).strip()
                    start_idx = match.end()
                    search_area = text[start_idx:start_idx+150]
                    role_match = re.search(role_pattern, search_area, re.IGNORECASE)
                    
                    if role_match:
                        role = role_match.group(1).strip(" ()").title()
                        ticked_names.append(f"{name} ({role})")
                    else:
                        ticked_names.append(name)
                
                # 3. Regex for Ticked names (Pattern: 1. NAME √)
                matches_t2 = re.finditer(r'\d+\.[\s\n]*([A-Z\s]+?)[\s\n]*√', text, re.IGNORECASE)
                for match in matches_t2:
                    name = match.group(1).strip()
                    start_idx = match.end()
                    search_area = text[start_idx:start_idx+150]
                    role_match = re.search(role_pattern, search_area, re.IGNORECASE)
                    
                    if role_match:
                        # Fix title casing for numbers (e.g., "2Nd" -> "2nd")
                        role = role_match.group(1).strip(" ()").title().replace("1St", "1st").replace("2Nd", "2nd").replace("3Rd", "3rd").replace("4Th", "4th")
                        ticked_names.append(f"{name} ({role})")
                    else:
                        ticked_names.append(name)
                    
    except Exception as e:
        print(f"Error reading PDF: {e}")

    # Remove duplicates while keeping order
    def deduplicate(name_list):
        seen = set()
        final = []
        for name in name_list:
            if name not in seen:
                seen.add(name)
                final.append(name)
        return final

    final_ticked = deduplicate(ticked_names)
    final_reserve = deduplicate(reserve_names)

    print(f"Successfully extracted {len(final_ticked)} ticked names and {len(final_reserve)} reserve names.")
    
    # Write to GitHub Step Summary
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as sf:
            sf.write("## 📝 PDF Extraction Result\n\n")
            
            if final_ticked:
                for i, name in enumerate(final_ticked, 1):
                    sf.write(f"{i}. `{name}`\n")
            else:
                sf.write("No ticked names were found in the document.\n")
            
            sf.write("\n### Reserve:\n")
            if final_reserve:
                for i, name in enumerate(final_reserve, 1):
                    sf.write(f"{i}. `{name}`\n")
            else:
                sf.write("No reserve names were found in the document.\n")

if __name__ == '__main__':
    extract_name_from_pdf()
