
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path, include  # include is used to include app-level URLs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', include('pii_detector.urls')),  # Include the app's URLs here
]


