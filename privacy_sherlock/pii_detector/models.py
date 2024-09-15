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
