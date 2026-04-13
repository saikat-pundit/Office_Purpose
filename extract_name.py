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
    
    extracted_names = []
    
    try:
        # Read the downloaded PDF
        with open(output, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Loop through ALL pages in the PDF
            for page in reader.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                # Regex 1: Looks for "√" followed by newlines/spaces, a number, a dot, and the Name.
                # Using finditer to catch multiple instances if they exist on the same page.
                matches = re.finditer(r'√\s*\n?\s*\d+\.\s*([A-Z\s]+?)(?=\n|ASSISTANT|PRIMARY|LIBRARIAN|OFFICE|HEAD TEACHER)', text, re.IGNORECASE)
                for match in matches:
                    extracted_names.append(match.group(1).strip())
                
                # Regex 2: Fallback in case it's perfectly inline like "3. AMIT GHOSH √"
                matches_inline = re.finditer(r'\d+\.\s*([A-Z\s]+?)\s*√', text)
                for match in matches_inline:
                    extracted_names.append(match.group(1).strip())
                    
    except Exception as e:
        print(f"Error reading PDF: {e}")

    # Remove any potential duplicates while keeping the original order
    seen = set()
    final_names = []
    for name in extracted_names:
        if name not in seen:
            seen.add(name)
            final_names.append(name)

    print(f"Successfully extracted {len(final_names)} names.")
    
    # Write to GitHub Step Summary to display in the Actions UI
    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as sf:
            sf.write("## 📝 PDF Extraction Result\n")
            if final_names:
                for i, name in enumerate(final_names, 1):
                    sf.write(f"{i}. `{name}`\n")
            else:
                sf.write("No ticked names were found in the document.\n")

if __name__ == '__main__':
    extract_name_from_pdf()
