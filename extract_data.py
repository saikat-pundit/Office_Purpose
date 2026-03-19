import re
import csv
import PyPDF2

def parse_pdf_to_csv(pdf_path, csv_path):
    # Define the headers for your CSV
    headers = [
        "Name", "Designation", "Mobile Number", "Trainee Code", 
        "Training Venue", "Training Date", "Training Time", 
        "EPIC No", "Part No", "Sl No", "Assembly Constituency", 
        "Account Number", "IFSC"
    ]
    
    data_rows = []
    
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Iterate through every page
        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue
                
            # Regex patterns to extract specific fields
            # Name, Designation, and Mobile
            name_match = re.search(r'Name of.*?Officer\s+(.*?),\s*(.*?),\s*MOBILE NO:\s*(\d+)', text, re.IGNORECASE)
            
            # Trainee Code
            trainee_match = re.search(r'Trainee Code:\s*([A-Z0-9\-]+/\d+)', text)
            
            # Training Venue, Date, and Time
            venue_match = re.search(r'Venue & Address\s*Date & Time\s*(.*?)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}\s*[AP]M\s*to\s*\d{2}:\d{2}\s*[AP]M)', text, re.DOTALL)
            
            # EPIC, Part No, Sl No
            epic_match = re.search(r'EPIC No\.\s*-\s*([A-Z0-9]+).*?Part No\.\s*-\s*(\d+).*?Sl\. No\.\s*-\s*(\d+)', text, re.DOTALL)
            
            # Assembly Constituency
            assembly_match = re.search(r'Permanent Assembly Constituency\s*-\s*(.*)', text)
            
            # Account No and IFSC
            bank_match = re.search(r'A/c No\.\s*-\s*(\d+).*?IFSC\s*-\s*([A-Z0-9]+)', text, re.DOTALL)
            
            # If a name is found, it's a valid appointment letter page
            if name_match:
                venue_text = venue_match.group(1).strip().replace('\n', ' ') if venue_match else ""
                
                row = {
                    "Name": name_match.group(1).strip(),
                    "Designation": name_match.group(2).strip(),
                    "Mobile Number": name_match.group(3).strip(),
                    "Trainee Code": trainee_match.group(1).strip() if trainee_match else "",
                    "Training Venue": venue_text,
                    "Training Date": venue_match.group(2).strip() if venue_match else "",
                    "Training Time": venue_match.group(3).strip() if venue_match else "",
                    "EPIC No": epic_match.group(1).strip() if epic_match else "",
                    "Part No": epic_match.group(2).strip() if epic_match else "",
                    "Sl No": epic_match.group(3).strip() if epic_match else "",
                    "Assembly Constituency": assembly_match.group(1).strip() if assembly_match else "",
                    "Account Number": bank_match.group(1).strip() if bank_match else "",
                    "IFSC": bank_match.group(2).strip() if bank_match else ""
                }
                data_rows.append(row)
                
    # Write the extracted data to data.csv
    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_rows)
        print(f"Successfully extracted {len(data_rows)} records to {csv_path}")

if __name__ == "__main__":
    # Expects the PDF to be in the same folder, outputs to data.csv
    parse_pdf_to_csv('appointment_letters.pdf', 'data.csv')
