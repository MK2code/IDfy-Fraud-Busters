
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path, include  # include is used to include app-level URLs

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('ingest/', ingest_data, name='ingest-data'),
    # path('visualize/', visualize_pii_risk, name='visualize-pii-risk'),
    path('upload/', include('pii_detector.urls')),  # Include the app's URLs here
]


