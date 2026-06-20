from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('doctor/', include('doctors.urls')),
    path('patient/', include('patients.urls')),
    path('admin-dashboard/', include('admin_dashboard.urls')),
]