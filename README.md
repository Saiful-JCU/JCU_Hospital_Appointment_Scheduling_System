# Hospital Appointment Scheduling System

A complete **Hospital Appointment Scheduling System** built with **Django**, designed for university final project submission.
The system supports **patients**, **doctors**, and **admin** roles with appointment booking, doctor scheduling, consultation notes, patient history, blogs, contact form, and admin reporting features.

---

# 1. Project Overview

The **Hospital Appointment Scheduling System** is a web-based application that helps manage the daily workflow of a hospital.
It allows:

* **Patients** to browse doctors, book appointments, view their appointments, and read consultation notes.
* **Doctors** to manage schedules, appointments, patient notes, and patient history.
* **Admins** to manage doctors, patients, departments, and reports.

The main goal of this project is to reduce manual hospital appointment management and provide a clean digital workflow for all users.

---

# 2. Features

---

## 2.1 Patient Features

* Patient registration and login
* Browse doctors by:

  * specialty / department
  * city
  * doctor name
* View doctor available slots
* Book appointment
* Cancel appointment
* Reschedule appointment
* View appointment history
* View private consultation notes written by doctor
* View personal dashboard
* Contact hospital through contact form
* Read hospital blogs

---

## 2.2 Doctor Features

* Doctor login
* Doctor dashboard
* View own appointments
* Create schedule / slot
* Toggle slot availability
* View patient list
* Add private consultation notes for a patient
* View all consultation notes created by the doctor
* View complete patient history:

  * patient profile
  * previous appointments
  * consultation notes

---

## 2.3 Admin Features

* Admin dashboard
* Manage doctors

  * add doctor
  * edit doctor
  * delete doctor
* Manage departments / specialties

  * add department
  * edit department
  * delete department
* Manage patients

  * patient list
  * patient detail
  * delete patient
* Reports

  * total appointments
  * appointments per day
  * appointments per week
  * daily patient flow

---

## 2.4 Public Website Features

* Landing page
* Browse doctors page
* Blog list / blog carousel
* Contact page
* Login / register

---

# 3. Technology Stack

* **Backend:** Django
* **Frontend:** HTML, CSS, Bootstrap, Django Template Language
* **Database:** SQLite
* **Authentication:** Django authentication system
* **Charts / Reports:** Chart.js
* **Media Upload:** Django ImageField

---

# 4. System Users

The system has **three main user roles**:

1. **Patient**
2. **Doctor**
3. **Admin**

---

# 5. Project Structure

```bash
Hospital-Management/
│
├── hospital/                  # Main project settings
├── users/                     # User management app
├── patients/                  # Patient features app
├── doctors/                   # Doctor features app
├── blogs/                     # Blog app
├── admin_dashboard/           # Admin dashboard app
├── templates/                 # HTML templates
├── static/                    # CSS / JS / images
├── media/                     # Uploaded media files
├── db.sqlite3                 # Database
└── manage.py
```

---

# 6. Apps and Responsibilities

---

## 6.1 `users` app

Handles all user-related data.

### Main responsibilities:

* custom user model
* doctor model
* patient model
* specialty / department
* address
* contact form model

### Main models:

* `Users`
* `Doctors`
* `Patients`
* `Specialty`
* `Address`
* `Contact`

---

## 6.2 `patients` app

Handles patient-side features.

### Main responsibilities:

* patient dashboard
* browse doctors
* book appointment
* view appointments
* cancel / reschedule appointment

### Main models / related data:

* `Appointment`
* doctor schedules
* patient booking flow

---

## 6.3 `doctors` app

Handles doctor-side features.

### Main responsibilities:

* doctor dashboard
* doctor schedules
* appointment management
* consultation notes
* patient history

### Main models:

* `DoctorSchedule`
* `ConsultationNote`

---

## 6.4 `blogs` app

Handles hospital / doctor blog system.

### Main responsibilities:

* blog categories
* doctor blog posts
* comments

### Main models:

* `Category`
* `Blogs`
* `Comments`

---

## 6.5 `admin_dashboard` app

Handles hospital admin management.

### Main responsibilities:

* doctor management
* department management
* patient management
* reports dashboard

---

# 7. Database Models

Below is the core model design used in the project.

---

# 7.1 Users Model

```python
class Users(AbstractUser):
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=200)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender_choices = (("Male", "Male"), ("Female", "Female"))
    gender = models.CharField(max_length=10, choices=gender_choices, default="not_known")
    birthday = models.DateField(null=True, blank=True)
    is_doctor = models.BooleanField(default=False)
    profile_avatar = models.ImageField(upload_to="users/profiles", blank=True, default="doctor/profiles/download.png")
    id_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
```

### Purpose

Stores the main authentication and profile data for all system users.

---

# 7.2 Doctors Model

```python
class Doctors(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    bio = models.TextField()
```

### Purpose

Stores doctor-specific information linked to the main user.

---

# 7.3 Patients Model

```python
class Patients(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    insurance = models.CharField(max_length=50)
```

### Purpose

Stores patient-specific information linked to the main user.

---

# 7.4 Appointment Model

```python
class Appointment(models.Model):
    schedule = models.OneToOneField(DoctorSchedule, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    summary = models.TextField()
    description = models.TextField()
    start_date = models.DateField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, default=1)

    class Meta:
        unique_together = ('doctor', 'start_date', 'time')
```

### Purpose

Stores appointment booking information between patient and doctor.

---

# 7.5 DoctorSchedule Model

```python
class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, related_name="schedules")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Purpose

Stores doctor’s available schedule slots.

---

# 7.6 ConsultationNote Model

```python
class ConsultationNote(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, related_name="consultation_notes")
    patient = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="patient_notes")
    title = models.CharField(max_length=200)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
```

### Purpose

Stores private consultation notes written by a doctor for a patient.

### Security rule

Only:

* the doctor who created the note
* the related patient

can view the note.

---

# 7.7 Blogs Model

```python
class Blogs(models.Model):
    blog_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    summary = models.TextField()
    is_published = models.BooleanField(default=False)
    posted_at = models.DateField(default=datetime.now)
    thumbnail = models.ImageField(upload_to="blogs/thumbnail", null=True, blank=True)
    id_category = models.ForeignKey(Category, on_delete=models.PROTECT)
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
```

### Purpose

Stores blog posts written by doctors or hospital content managers.

---

# 7.8 Contact Model

### Purpose

Stores contact form messages submitted from the public website.

Typical fields:

* name
* email
* subject
* message
* created_at

---

# 8. Main Functional Modules

---

# 8.1 Authentication Module

Supports:

* login
* logout
* patient registration
* doctor/admin access control

### Role-based dashboard logic

* if user is doctor → doctor dashboard
* if user is patient → patient dashboard
* if user is staff/admin → admin dashboard

---

# 8.2 Doctor Browsing and Appointment Booking

Patients can browse doctors using filters:

* specialty
* city
* doctor name

Each doctor card shows:

* doctor name
* specialty
* bio / short info
* whether doctor has available slots

If the doctor has available schedule slots:

* patient can click **View Slots**
* patient can proceed to appointment booking

---

# 8.3 Doctor Schedule Management

Doctors can:

* create schedule slots
* view all schedule slots
* mark slot available / unavailable
* manage their appointment times

This ensures that patients only book from valid doctor schedules.

---

# 8.4 Consultation Notes Module

After consultation, the doctor can add a private note for the patient.

Each note contains:

* note title
* detailed consultation note
* doctor
* patient
* creation time

### Access rules

* Doctor can create notes for patients from appointment history
* Doctor can see notes they created
* Patient can see only their own notes
* Other patients cannot access these notes

---

# 8.5 Patient History Module

Doctors can open a **patient history page** and view:

### Patient profile

* full name
* username
* email
* gender
* date of birth
* insurance
* address
* profile image

### Appointment history

* all previous appointments
* appointment date
* doctor
* status
* summary / description

### Consultation notes

* all consultation notes for that patient

This helps the doctor review the patient’s medical and appointment history before consultation.

---

# 8.6 Blog Module

The landing page includes a simple blog section / carousel.

Blog features:

* show published blogs
* show blog thumbnail
* show blog summary
* open full blog details

---

# 8.7 Contact Module

Users can submit contact requests from the public website.

The system stores:

* sender name
* sender email
* subject
* message

Admins can review submitted messages in the Django admin panel.

---

# 8.8 Admin Dashboard Module

Admin can manage the full hospital system.

### Doctor Management

* list all doctors
* add doctor
* edit doctor
* delete doctor

### Department Management

* list all departments
* add department
* edit department
* delete department

### Patient Management

* list all patients
* patient detail page
* delete patient

### Reports

* report dashboard summary
* appointments per day
* appointments per week
* daily patient flow

---

# 9. Reporting Module

The reporting system helps hospital admins monitor system activity.

---

## 9.1 Report Dashboard

Shows quick overview of:

* total appointments
* today appointments
* weekly appointments
* total patients today

---

## 9.2 Appointments Per Day

Groups appointments by `start_date` and counts total appointments for each day.

Example:

| Date       | Total Appointments |
| ---------- | ------------------ |
| 2026-06-18 | 5                  |
| 2026-06-19 | 7                  |

---

## 9.3 Appointments Per Week

Shows appointment totals for each day of the current week.

Example:

| Date       | Day     | Total Appointments |
| ---------- | ------- | ------------------ |
| 2026-06-15 | Monday  | 3                  |
| 2026-06-16 | Tuesday | 4                  |

---

## 9.4 Daily Patient Flow

Shows number of **unique patients per day**.

Example:

| Date       | Total Unique Patients |
| ---------- | --------------------- |
| 2026-06-18 | 4                     |
| 2026-06-19 | 6                     |

---

# 10. Important Security Rules

This project uses role-based access control.

---

## 10.1 Patient Security

A patient can:

* book own appointments
* view own appointments
* view own consultation notes

A patient **cannot**:

* see another patient’s notes
* see another patient’s appointment history
* access doctor/admin pages

---

## 10.2 Doctor Security

A doctor can:

* manage own schedule
* view own appointments
* add consultation notes for patients
* view patient history of linked patients

A doctor **cannot**:

* access admin-only pages
* manage another doctor’s schedule

---

## 10.3 Admin Security

Admin can:

* manage doctors
* manage departments
* manage patients
* view system reports

Admin routes are protected using `staff_member_required`.

---

# 11. Important Views in the Project

Below are the main views created in the system.

---

## 11.1 Patient Views

* `patient_dashboard`
* `book_appointment`
* `my_appointments`
* `cancel_appointment`
* `reschedule_appointment`
* `patient_notes`

---

## 11.2 Doctor Views

* `doctor_dashboard`
* `view_appointments`
* `create_schedule`
* `doctor_schedule_list`
* `toggle_schedule`
* `patient_list`
* `add_consultation_note`
* `doctor_notes`
* `patient_history`

---

## 11.3 Admin Dashboard Views

* `admin_dashboard_home`
* `admin_doctor_list`
* `admin_doctor_create`
* `admin_doctor_update`
* `admin_doctor_delete`
* `admin_department_list`
* `admin_department_create`
* `admin_department_update`
* `admin_department_delete`
* `admin_patient_list`
* `admin_patient_detail`
* `admin_patient_delete`
* `report_dashboard`
* `appointments_per_day_report`
* `appointments_per_week_report`
* `daily_patient_flow_report`

---

# 12. URL Design

The project uses separate URL groups for each app.

Example structure:

```python
path('', include('users.urls'))
path('patient/', include('patients.urls'))
path('doctor/', include('doctors.urls'))
path('admin-dashboard/', include('admin_dashboard.urls'))
path('blogs/', include('blogs.urls'))
```

---

# 13. UI / Template Structure

The project uses Django templates with a separate layout for:

* landing page
* patient dashboard
* doctor dashboard
* admin dashboard

Common template sections:

* navbar
* sidebar
* dashboard cards
* tables
* forms
* charts
* footer

---

# 14. How the Booking Flow Works

1. Patient logs in
2. Patient opens doctor browsing page
3. Patient filters doctor list if needed
4. Patient clicks **View Slots**
5. Available doctor schedule slots are shown
6. Patient books a slot
7. Appointment record is created
8. Doctor sees appointment in doctor dashboard / appointment list
9. After consultation, doctor can write consultation notes
10. Patient can view their own notes later

---

# 15. How the Consultation Note Flow Works

1. Doctor opens patient list
2. Doctor selects a patient
3. Doctor clicks **Add Note**
4. Doctor writes:

   * title
   * notes
5. Note is saved in `ConsultationNote`
6. Doctor can later view all notes from **My Notes**
7. Patient can see only notes linked to their own user account

---

# 16. How the Patient History Flow Works

1. Doctor opens patient list
2. Doctor clicks **Patient History**
3. System loads:

   * patient profile
   * all appointments of that patient
   * all consultation notes for that patient
4. Doctor reviews history before treatment

---

# 17. Admin Report Logic

---

## Appointments per day

```python
Appointment.objects.values("start_date").annotate(total=Count("pk"))
```

---

## Daily patient flow

```python
Appointment.objects.values("start_date").annotate(
    total_patients=Count("patient", distinct=True)
)
```

---

## Weekly appointments

Appointments are grouped inside a date range from **Monday to Sunday**.

---

# 18. Installation Guide

## Step 1: Clone project

```bash
git clone <your-repository-url>
cd Hospital-Management
```

## Step 2: Create virtual environment

```bash
python -m venv venv
```

## Step 3: Activate virtual environment

### Windows

```bash
venv\Scripts\activate
```

### Mac / Linux

```bash
source venv/bin/activate
```

## Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 6: Create superuser

```bash
python manage.py createsuperuser
```

## Step 7: Run server

```bash
python manage.py runserver
```

---

# 19. Example Requirements

Typical packages used:

```txt
Django
Pillow
```

If using chart/report or extra tools, include them as needed in `requirements.txt`.

---

# 20. Admin Credentials

Use the superuser account created by:

```bash
python manage.py createsuperuser
```

Then log in to:

```bash
http://127.0.0.1:8000/admin/
```

---

# 21. Future Improvements

Possible future improvements for the system:

* payment integration
* email notification for appointments
* SMS reminder system
* prescription module
* downloadable medical report
* doctor rating / review system
* online meeting / telemedicine
* medicine reminder system
* PDF report export
* advanced analytics dashboard

---

# 22. Challenges Faced During Development

Some common issues faced during development:

* URL reverse errors (`NoReverseMatch`)
* role-based access control bugs
* linking `Users`, `Doctors`, and `Patients` properly
* appointment slot filtering and availability checks
* consultation note privacy handling
* report queries not showing data because of wrong queryset logic
* dashboard templates requiring dynamic Django context data

These issues were solved by:

* fixing URL parameters
* using correct model relationships
* checking user role before view access
* using grouped report queries properly
* designing secure patient/doctor note access

---

# 23. Learning Outcomes

This project helped practice:

* Django models and relationships
* Django forms and views
* authentication and authorization
* role-based dashboard design
* appointment scheduling logic
* report generation with querysets
* template rendering and dashboard UI design
* CRUD operations for admin panels
* hospital workflow system design

---

# 24. Conclusion

The **Hospital Appointment Scheduling System** is a complete university-level Django web application that digitizes hospital operations for patients, doctors, and administrators.

It includes:

* doctor browsing and appointment booking
* doctor schedule management
* consultation note system
* patient history system
* blogs and contact page
* admin dashboard with reports

The system demonstrates practical use of Django for a real-world healthcare workflow and can be extended further into a larger hospital management platform.

---

# 25. Author
**Developed By:** Khan Md Saiful Islam
**Project Name:** Hospital Appointment Scheduling System
**Framework:** Django
**Project Type:** University Final Assignment / Semester Project

Prepared as an academic hospital management system project.
