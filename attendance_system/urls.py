# FILE: attendance_system/urls.py

from django.contrib import admin
from django.urls import path, include  # <-- 1. Import 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 2. Add this line to link to your app's urls.py file
    path('', include('attendance_app.urls')), 
]