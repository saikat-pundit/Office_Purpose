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
    
    extracted_name = "Name not found"
    
    try:
        # Read the downloaded PDF
        with open(output, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                
                # Regex 1: Looks for "√" followed by newlines/spaces, a number, a dot, and the Name.
                # It stops capturing before the designation (e.g., ASSISTANT) or a newline.
                match = re.search(r'√\s*\n?\s*\d+\.\s*([A-Z\s]+?)(?=\n|ASSISTANT|PRIMARY|LIBRARIAN|OFFICE)', text, re.IGNORECASE)
                
                if match:
                    extracted_name = match.group(1).strip()
                    break
                
                # Regex 2: Fallback in case it's perfectly inline like "3. AMIT GHOSH √"
                match_inline = re.search(r'\d+\.\s*([A-Z\s]+?)\s*√', text)
                if match_inline:
                    extracted_name = match_inline.group(1).strip()
                    break
                    
    except Exception as e:
        print(f"Error reading PDF: {e}")

    print(f"Successfully extracted: {extracted_name}")
    
    # Write to GitHub Step Summary to display in the Actions UI
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as sf:
            sf.write("## 📝 PDF Extraction Result\n")
            sf.write(f"**Extracted Name:** `{extracted_name}`\n")

if __name__ == '__main__':
    extract_name_from_pdf()
