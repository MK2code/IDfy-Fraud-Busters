
markdown
Copy code
# PII Detection Django Project

## 📜 Project Overview

This Django project is designed to allow users to upload various types of files (text, PDF, Excel) and perform PII (Personally Identifiable Information) detection on the uploaded content. It uses the Presidio library for PII detection and anonymization.

## 🚀 Getting Started

### 🔧 Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.8+
- Django 3.2+
- pip (Python package installer)

### 📥 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/pii-detection-django.git
   cd pii-detection-django
Create a Virtual Environment

bash
Copy code
python -m venv venv
Activate the Virtual Environment

On Windows:

bash
Copy code
venv\Scripts\activate
On macOS/Linux:

bash
Copy code
source venv/bin/activate
Install the Required Packages

bash
Copy code
pip install -r requirements.txt
Add the following to your requirements.txt file:

makefile
Copy code
Django==4.0.1
presidio-analyzer==2.0.0
presidio-anonymizer==2.0.0
spacy==3.1.0
Download SpaCy Model

bash
Copy code
python -m spacy download en_core_web_lg
Apply Database Migrations

bash
Copy code
python manage.py migrate
Create a Superuser

bash
Copy code
python manage.py createsuperuser
Run the Development Server

bash
Copy code
python manage.py runserver
Open your browser and navigate to http://127.0.0.1:8000 to see the project in action.

🛠️ Project Structure
views.py: Contains the logic for handling file uploads, PII detection, and anonymization.
forms.py: Defines the file upload form and its fields.
models.py: Contains the database models for storing data sources and PII information.
utils.py: Utility functions for processing files and detecting PII.
upload.html: The HTML template for file upload.
📄 Code Highlights
📂 views.py
Handles file uploads and processes them based on file type.

python
Copy code
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from .utils import detect_pii, anonymize_text, process_pdf_to_text, process_excel_to_text
from .models import DataSource, PiiData

def upload_files(request):
    if request.method == 'GET':
        form = FileUploadForm()
        return render(request, 'pii_detector/upload.html', {'form': form})

    elif request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('file')
            file_type = form.cleaned_data.get('file_type')  # File type selection

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
                data_source = DataSource.objects.create(source_name=file.name, source_type=file_type)

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
📂 forms.py
Defines the file upload form with a file_type selection.

python
Copy code
from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class FileUploadForm(forms.Form):
    file_type = forms.ChoiceField(
        choices=[('text', 'Text'), ('pdf', 'PDF'), ('excel', 'Excel')],
        required=True,
        label="Select file type"
    )
    file = MultipleFileField(label='Select files')
📂 models.py
Defines the database models for storing file and PII data.

python
Copy code
from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent_folder = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class File(models.Model):
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='files/')
    text_file_path = models.CharField(max_length=255, blank=True)

class DataSource(models.Model):
    source_name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=255)  # e.g., 'S3', 'SQL'
    ingest_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.source_name

class PiiData(models.Model):
    pii_type = models.CharField(max_length=255)  # e.g., 'SSN', 'Email'
    pii_value = models.TextField()
    pii_risk_score = models.FloatField()
    pii_category = models.CharField(max_length=255)  # e.g., 'financial', 'personal'
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='pii_data')

    def __str__(self):
        return f'{self.pii_type}: {self.pii_value}'
📂 upload.html
The HTML template for file uploads.

html
Copy code
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Upload Files</button>
</form>

{% if error %}
    <p style="color: red;">{{ error }}</p>
{% endif %}

{% if results %}
    <h2>Results:</h2>
    <ul>
        {% for result in results %}
            <li>
                <strong>{{ result.file_name }}</strong>
                <h3>PII Detected:</h3>
                <ul>
                    {% for pii in result.pii_detected %}
                        <li>{{ pii.type }}: {{ pii.value }}</li>
                    {% endfor %}
                </ul>
                <h3>Anonymized Text:</h3>
                <pre>{{ result.anonymized_text }}</pre>
            </li>
        {% endfor %}
    </ul>
{% endif %}
📜 Usage
Upload Files: Navigate to the home page, select the file type, choose your files, and click "Upload Files."
View Results: After uploading, the page will show detected PII and anonymized text.
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🛠️ Troubleshooting
Error Handling: If you encounter issues, check the console for error messages and ensure all dependencies are installed correctly.
File Types: Ensure you select the correct file type (Text, PDF, Excel) when uploading.
🧑‍💻 Contributing
Feel free to fork the repository, make changes, and submit pull requests. For any issues or feature requests, please open an issue on the GitHub Issues page.
