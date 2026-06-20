from django.urls import path
from .views import browse_doctors, home, blog, register, login_view, forgot_view, reset_view, logout_view, doctor_slots
from .views import contact_view
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', home, name='index'),
    path('doctor/<int:doctor_id>/slots/', doctor_slots, name='doctor_slots'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('password-reset/', forgot_view, name='password-reset'),
    path('reset/<str:token>/', reset_view, name='reset'),
    path('logout/', logout_view, name='logout'),

    path('browse-doctors/', browse_doctors, name='browse_doctors'),
    path('blogs/', blog, name='blogs'),

    path("contact/", contact_view, name="contact"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns+=staticfiles_urlpatterns()