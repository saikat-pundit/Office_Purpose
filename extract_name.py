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
    
    try:
        # Read the downloaded PDF
        with open(output, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Loop through ALL pages in the PDF
            for page in reader.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Check for Reserve (RSV) names
                rsv_match = re.search(r'RSV[^a-zA-Z]*([A-Z\s]+?)[,\n]', text)
                if rsv_match:
                    reserve_names.append(rsv_match.group(1).strip())
                    continue 
                
                # Regex 1: Looks for "√" followed by newlines/spaces, a number, a dot, and the Name.
                matches = re.finditer(r'√\s*\n?\s*\d+\.\s*([A-Z\s]+?)(?=\n|ASSISTANT|PRIMARY|LIBRARIAN|OFFICE|HEAD TEACHER)', text, re.IGNORECASE)
                found_ticked = False
                for match in matches:
                    ticked_names.append(match.group(1).strip())
                    found_ticked = True
                
                if found_ticked:
                    continue
                
                # Regex 2: Fallback in case it's perfectly inline like "3. AMIT GHOSH √"
                matches_inline = re.finditer(r'\d+\.\s*([A-Z\s]+?)\s*√', text)
                for match in matches_inline:
                    ticked_names.append(match.group(1).strip())
                    
    except Exception as e:
        print(f"Error reading PDF: {e}")

    # Remove any potential duplicates while keeping the original order
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
    
    # Write to GitHub Step Summary to display in the Actions UI
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
