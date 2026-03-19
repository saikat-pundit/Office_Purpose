import re
import csv
import PyPDF2
import gdown
import os

def download_from_drive(file_id, output_path):
    print(f"Downloading file from Google Drive...")
    url = f'https://drive.google.com/uc?id={file_id}'
    gdown.download(url, output_path, quiet=False)
    print("Download complete.")

def parse_pdf_to_csv(pdf_path, csv_path):
    # Added new headers for all the additional details
    headers = [
        "Name", "Designation", "Mobile Number", "Order No", "Order Date", 
        "Office Details", "Post Status", "Training Name", "Trainee Code", 
        "Training Venue", "Training Date", "Training Time", 
        "EPIC No", "Part No", "Sl No", "Assembly Constituency", 
        "Account Number", "IFSC"
    ]
    
    data_rows = []
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue
                
            # 1. Name, Designation, and Mobile
            name_match = re.search(r'Name of.*?Officer\s+(.*?),\s*(.*?),\s*MOBILE NO:\s*(\d+)', text, re.IGNORECASE)
            
            # 2. Order No and Date
            order_match = re.search(r'Order No:\s*(.*?)\nDate:\s*([^\n]+)', text)
            
            # 3. Office Details and Post Status
            office_match = re.search(r'OFFICE DETAILS\s*-\s*(.*?)\nPost Status\s*-\s*([^\n]+)', text, re.DOTALL)
            
            # 4. Training Details
            training_name_match = re.search(r'Training\n([^\n]+)\nTrainee Code:', text)
            trainee_match = re.search(r'Trainee Code:\s*([A-Z0-9\-]+/\d+)', text)
            venue_match = re.search(r'Venue & Address\s*Date & Time\s*(.*?)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}\s*[AP]M\s*to\s*\d{2}:\d{2}\s*[AP]M)', text, re.DOTALL)
            
            # 5. Electoral and Bank Data (Added slashes '/' in EPIC Regex)
            epic_match = re.search(r'EPIC No\.\s*-\s*([A-Z0-9/]+).*?Part No\.\s*-\s*(\d+).*?Sl\. No\.\s*-\s*(\d+)', text, re.DOTALL)
            assembly_match = re.search(r'Permanent Assembly Constituency\s*-\s*([^\n]+)', text)
            bank_match = re.search(r'A/c No\.\s*-\s*(\d+).*?IFSC\s*-\s*([A-Z0-9]+)', text, re.DOTALL)
            
            if name_match:
                # Clean up multiline address spaces
                venue_text = venue_match.group(1).strip().replace('\n', ', ') if venue_match else ""
                office_text = office_match.group(1).strip().replace('\n', ' ') if office_match else ""
                
                row = {
                    "Name": name_match.group(1).strip(),
                    "Designation": name_match.group(2).strip(),
                    "Mobile Number": name_match.group(3).strip(),
                    "Order No": order_match.group(1).strip() if order_match else "",
                    "Order Date": order_match.group(2).strip() if order_match else "",
                    "Office Details": office_text,
                    "Post Status": office_match.group(2).strip() if office_match else "",
                    "Training Name": training_name_match.group(1).strip() if training_name_match else "",
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
                
    with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_rows)
        print(f"Successfully extracted {len(data_rows)} records to {csv_path}")

if __name__ == "__main__":
    DRIVE_FILE_ID = '1iRD1LrKu_oOLPos0UEBSqzFFnjp7XFfJ'
    LOCAL_PDF_PATH = 'temp_appointment_letters.pdf'
    OUTPUT_CSV_PATH = 'data.csv'
    
    download_from_drive(DRIVE_FILE_ID, LOCAL_PDF_PATH)
    
    if os.path.exists(LOCAL_PDF_PATH):
        parse_pdf_to_csv(LOCAL_PDF_PATH, OUTPUT_CSV_PATH)
        os.remove(LOCAL_PDF_PATH)
    else:
        print("Error: PDF file was not downloaded successfully.")
