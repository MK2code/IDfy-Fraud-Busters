# PII Detection Django Project

## Introduction

This Django project allows users to upload files (text, PDF, Excel) and performs PII (Personally Identifiable Information) detection using the Presidio library. It supports text extraction, PII detection, and anonymization.

## Requirements

- Python 3.8+
- Django 4.0+
- Presidio Analyzer and Anonymizer
- SpaCy with `en_core_web_lg` model

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/pii-detection-django.git
   cd pii-detection-django

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate for Windows

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   
4. Download the SpaCy model:

   ```bash
   python -m spacy download en_core_web_lg

5. Apply migrations and create a superuser:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser

6. Run the server:

   ```bash
   python manage.py runserver

## Usage

1. Navigate to http://127.0.0.1:8000 in your browser.
   
2. Use the form to upload files and select the file type (text, PDF, Excel).
   
3. View the detected PII and anonymized results on the same page after upload.

   
## Usage

After processing, the results include:
   **Detected PII**: Types and values of PII detected in the file.
   **Anonymized Text**: The text with PII anonymized.


