import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from django.shortcuts import render, redirect

import os
from .forms import FileUploadForm
from .utils import detect_pii, anonymize_text, process_pdf_to_text, classify_pii,calculate_risk
from .models import DataSource, PiiData

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def process_pdf_to_text(pdf_file):
    # Convert PDF to text using OCR
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    )
    pdf_path = os.path.splitext(pdf_file.name)
    pdf_name = pdf_path[0]
    images = convert_from_path(pdf_file.temporary_file_path(), poppler_path=r"C:\Users\kumaw\Desktop\Website\project\poppler\Library\bin")
    text_content = ""
    for image in images:
        text = pytesseract.image_to_string(image)
        text_content += text
    return text_content

def process_excel_to_text(excel_file):
    # Extract text from Excel
    df = pd.read_excel(excel_file)
    text_content = df.to_string(index=False)
    return text_content

def process_text_file(text_file):
    return text_file.read().decode('utf-8')



def upload_files(request):
    if request.method == 'GET':
        form = FileUploadForm(None)  # Pass None instead of request.user
        return render(request, 'pii_detector/upload.html', {'form': form})

    elif request.method == 'POST':
        form = FileUploadForm(None, request.POST, request.FILES)  # Pass None for user
        if form.is_valid():
            files = request.FILES.getlist('file')
            file_type = form.cleaned_data.get('file_type')  # Assume 'file_type' field is added to form
            results = []

            for file in files:
                if file_type == 'text':
                    text_content = file.read().decode('utf-8')
                elif file_type == 'pdf':
                    text_content = process_pdf_to_text(file)
                elif file_type == 'excel':
                    text_content = process_excel_to_text(file)
                else:
                    return render(request, 'pii_detector/upload.html', {'form': form, 'error': 'Unsupported file type'})

                # Detect PII
                pii_detected = detect_pii(text_content)

                # Create DataSource entry
                folder_name = form.cleaned_data['new_folder_name'] or form.cleaned_data['folder'].name
                data_source = DataSource.objects.create(source_name=folder_name, source_type=file_type)

                # Save PII data
                for pii in pii_detected:
                    pii_type = pii['type']
                    pii_value = pii['value']
                    pii_category = classify_pii(pii_type)
                    pii_risk = calculate_risk(pii_type)

                    PiiData.objects.create(
                        pii_type=pii_type,
                        pii_value=pii_value,
                        pii_risk_score=pii_risk,
                        pii_category=pii_category,
                        data_source=data_source
                    )
                
                # Anonymize Text
                analyzer_results = analyzer.analyze(text=text_content, language='en')
                anonymized_text = anonymize_text(text_content, analyzer_results)
                
                results.append({
                    'file_name': file.name,
                    'pii_detected': pii_detected,
                    'anonymized_text': anonymized_text
                })

            return render(request, 'pii_detector/upload.html', {'form': form, 'results': results})
        
        return render(request, 'pii_detector/upload.html', {'form': form, 'error': 'Invalid form submission'})
