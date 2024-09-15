from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import json
import os
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from presidio_analyzer import BatchAnalyzerEngine, AnalyzerEngine
from presidio_anonymizer import BatchAnonymizerEngine

# Initialize batch analyzers and anonymizers
batch_analyzer = BatchAnalyzerEngine(analyzer_engine=AnalyzerEngine())
batch_anonymizer = BatchAnonymizerEngine()

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def detect_pii(text_content):
    # Detect PII entities
    analyzer_results = analyzer.analyze(text=text_content, language='en')
    
    # Convert to a list of dictionaries
    pii_detected = [{
        'type': result.entity_type,
        'value': text_content[result.start:result.end]
    } for result in analyzer_results]
    
    return pii_detected

def anonymize_text(text_content, analyzer_results):
    # Anonymize detected PII entities
    anonymized_results = anonymizer.anonymize(
        text=text_content,
        analyzer_results=analyzer_results,
        operators={
            "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"}),
            "PHONE_NUMBER": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 12, "from_end": True}),
            "TITLE": OperatorConfig("redact", {})
        }
    )
    return anonymized_results.text

# PII Classification based on type
def classify_pii(pii_type):
    classification_map = {
        'SSN': 'personal',
        'Email': 'personal',
        'Credit Card': 'financial',
        'PAN': 'financial',
    }
    return classification_map.get(pii_type, 'unknown')

# Risk Scoring for PII based on type
def calculate_risk(pii_type):
    risk_scores = {
        'SSN': 0.9,
        'Email': 0.4,
        'Credit Card': 0.8,
        'PAN': 0.7,
    }
    return risk_scores.get(pii_type, 0.1)  # Default risk score for unknown PII



# Function to handle processing PDFs
def process_pdf_to_text(pdf_file, folder_name):
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    images = convert_from_path(pdf_file.temporary_file_path(), poppler_path=r"C:\Users\kumaw\Desktop\Website\project\poppler\Library\bin")
    text_content = ""
    for image in images:
        text = pytesseract.image_to_string(image)
        text = text.replace("-\n", "")
        text_content += text
    
    text_file_path = save_text_to_file(folder_name, pdf_file.name, text_content)
    return text_file_path

# Function to handle text files
def process_text_file(text_file, folder_name):
    text_content = text_file.read().decode('utf-8')
    text_file_path = save_text_to_file(folder_name, text_file.name, text_content)
    return text_file_path

# Function to handle Excel files
def process_excel_file(excel_file, folder_name):
    df = pd.read_excel(excel_file)
    text_content = df.to_string(index=False)
    text_file_path = save_text_to_file(folder_name, excel_file.name, text_content)
    return text_file_path

# Utility function to save text to a file
def save_text_to_file(folder_name, file_name, text_content):
    text_file_path = os.path.join('media', 'text', folder_name, f'{os.path.splitext(file_name)[0]}.txt')
    os.makedirs(os.path.dirname(text_file_path), exist_ok=True)
    
    with open(text_file_path, 'w') as text_file:
        text_file.write(text_content)
    
    return text_file_path
def process_dataframe(df: pd.DataFrame):
    df_dict = df.to_dict(orient="list")  # Convert DataFrame to dictionary for analysis
    analyzer_results = list(batch_analyzer.analyze_dict(df_dict, language='en'))
    anonymizer_results = batch_anonymizer.anonymize_dict(analyzer_results)
    scrubbed_df = pd.DataFrame(anonymizer_results)
    return scrubbed_df

# Function to process JSON data
def process_json_data(json_data: dict):
    analyzer_results = list(batch_analyzer.analyze_dict(json_data, language='en'))
    anonymizer_results = batch_anonymizer.anonymize_dict(analyzer_results)
    return anonymizer_results
# Main function to process files
def process_uploaded_files(file, folder_name):
    if file.name.endswith('.pdf'):
        return process_pdf_to_text(file, folder_name)
    elif file.name.endswith('.txt'):
        return process_text_file(file, folder_name)
    elif file.name.endswith('.xlsx') or file.name.endswith('.csv'):
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        scrubbed_df = process_dataframe(df)
        return scrubbed_df.to_html()  # Convert DataFrame to HTML for display
    elif file.name.endswith('.json'):
        import json
        json_data = json.load(file)
        anonymized_json = process_json_data(json_data)
        return anonymized_json  # Return the processed JSON data
    else:
        raise ValueError("Unsupported file type")