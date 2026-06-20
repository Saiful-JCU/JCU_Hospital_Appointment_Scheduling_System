from django.urls import path
from .views import patient_dashboard, book_appointment, my_appointments, patient_confirm_book, cancel_appointment, reschedule_appointment
from doctors.views import doctor_blogs, search_blogs, profile, blogs_category, view_blog, post_comment
from .views import patient_confirm_book, my_consultation_notes, consultation_note_detail
from patients import views 

urlpatterns = [
  path('patient_dashboard/', patient_dashboard, name='patient_dashboard'),
  path('profile/', profile, name='patient_profile'),

  path('blogs/', doctor_blogs, name='patient_blogs'),
  path('search/', search_blogs, name='patient_search_blogs'),
  path('category/<str:cat>/', blogs_category, name='patient_categories'),
  path('blog/<int:blog_id>/', view_blog, name='patient_blog'),
  path('comment/', post_comment, name='patient_comment'),

  path('patient/book/<int:doctor_id>/', book_appointment, name='book_appointment'),
  # path('book_appointment/', book_appointment, name='book_appointment'),
  path('my_appointments/', my_appointments, name='my_appointments'),
  # path('patient_confirm_book/<str:doctor>/', patient_confirm_book, name='patient_confirm_book'),
  path( 'book/<int:schedule_id>/', patient_confirm_book, name='patient_confirm_book' ),
  path('cancel_appointment/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
  path('reschedule_appointment/<int:appointment_id>/', reschedule_appointment, name='reschedule_appointment'),


  path("my-consultation-notes/", my_consultation_notes, name="my_consultation_notes"),
  path("my-consultation-notes/<int:note_id>/", consultation_note_detail, name="consultation_note_detail"),
]
