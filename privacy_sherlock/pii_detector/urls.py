from django.urls import path
from .views import upload_files

urlpatterns = [
    path('', upload_files, name='upload-files'),  # Route to the upload page at /upload/
]
