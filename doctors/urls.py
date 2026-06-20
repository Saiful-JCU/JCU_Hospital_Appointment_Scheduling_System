from django.urls import path

from .views import  doctor_dashboard, doctor_schedule_list, patient_history, profile, doctor_blogs, search_blogs, blogs_category, view_blog, post_comment, doctor_drafts, upload_blog, doctor_myblogs, view_appointments
from .views import toggle_schedule, create_schedule, doctor_schedule_list, add_consultation_note, doctor_notes, patient_list



urlpatterns = [
  path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
  path('profile/', profile, name='doctor_profile'),
  path('doctor_blogs/', doctor_blogs, name='doctor_blogs'),
  path('search/',search_blogs,name='search_blogs'),
  path('category/<str:cat>/',blogs_category,name='categories'),
  path('upload_blog/', upload_blog,name="upload_blog"),
  path('blog/<int:blog_id>/',view_blog,name='blog'),
  path('comment/',post_comment,name='comment'),
  path('doctor_myblogs/', doctor_myblogs,name="myblogs"),
  path('doctor_drafts/',doctor_drafts , name='doctor_drafts'),
  path('upload_blog/<int:blog_id>/', upload_blog, name='upload_blog'),
  path('doctor_view_appointments/', view_appointments, name='view_appointments'),
  path( "schedule/create/", create_schedule, name="create_schedule" ),
  path( "schedule/", doctor_schedule_list, name="doctor_schedule_list" ),
  path( "schedule/<int:pk>/toggle/", toggle_schedule, name="toggle_schedule" ),


  path( "add_note/<int:patient_id>/", add_consultation_note, name="add_consultation_note" ),
  path("patients/", patient_list, name="doctor_patients"),
    path("my_notes/", doctor_notes, name="doctor_notes"),
    path("patient-history/<int:patient_id>/", patient_history, name="patient_history"),
]
