from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from users.models import Specialty, Doctors, Patients, Users, Address
from patients.models import Appointment
from .forms import SpecialtyForm, DoctorCreateForm, DoctorUpdateForm
from datetime import date, timedelta
from collections import OrderedDict


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login')
        if not request.user.is_staff:
            messages.error(request, "You are not allowed to access admin dashboard.")
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return wrapper



@login_required(login_url='/login')
@admin_required
def admin_dashboard_home(request):
    total_departments = Specialty.objects.count()
    total_doctors = Doctors.objects.count()
    total_patients = Patients.objects.count()
    total_appointments = Appointment.objects.count()

    context = {
        'total_departments': total_departments,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
    }
    return render(request, 'admin_dashboard/dashboard_home.html', context)



@login_required(login_url='/login')
@admin_required
def department_list(request):
    departments = Specialty.objects.all().order_by('name')

    return render(request, 'admin_dashboard/department_list.html', {
        'departments': departments
    })



@login_required(login_url='/login')
@admin_required
def department_add(request):
    if request.method == 'POST':
        form = SpecialtyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department added successfully.")
            return redirect('admin_department_list')
    else:
        form = SpecialtyForm()

    return render(request, 'admin_dashboard/department_form.html', {
        'form': form,
        'page_title': 'Add Department',
        'button_text': 'Add Department'
    })


@login_required(login_url='/login')
@admin_required
def department_edit(request, pk):
    department = get_object_or_404(Specialty, pk=pk)

    if request.method == 'POST':
        form = SpecialtyForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect('admin_department_list')
    else:
        form = SpecialtyForm(instance=department)

    return render(request, 'admin_dashboard/department_form.html', {
        'form': form,
        'page_title': 'Edit Department',
        'button_text': 'Update Department'
    })


@login_required(login_url='/login')
@admin_required
def department_delete(request, pk):
    department = get_object_or_404(Specialty, pk=pk)

    if request.method == 'POST':
        department.delete()
        messages.success(request, "Department deleted successfully.")
        return redirect('admin_department_list')

    return render(request, 'admin_dashboard/department_confirm_delete.html', {
        'department': department
    })


@login_required(login_url='/login')
@admin_required
def doctor_list(request):
    doctors = Doctors.objects.select_related('user', 'specialty').all().order_by('user__first_name')

    return render(request, 'admin_dashboard/doctor_list.html', {
        'doctors': doctors
    })


@login_required(login_url='/login')
@admin_required
def doctor_add(request):
    if request.method == 'POST':
        form = DoctorCreateForm(request.POST, request.FILES)
        if form.is_valid():
            # create address
            address = Address.objects.create(
                address_line=form.cleaned_data.get('address_line'),
                city=form.cleaned_data.get('city'),
                region=form.cleaned_data.get('region'),
                code_postal=form.cleaned_data.get('code_postal'),
            )

            # create user
            user = Users.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password']),
                gender=form.cleaned_data['gender'],
                birthday=form.cleaned_data.get('birthday'),
                is_doctor=form.cleaned_data.get('is_doctor', False),
                id_address=address,
            )

            # create doctor profile
            Doctors.objects.create(
                user=user,
                specialty=form.cleaned_data['specialty'],
                bio=form.cleaned_data.get('bio', '')
            )

            messages.success(request, "Doctor added successfully.")
            return redirect('admin_doctor_list')
    else:
        form = DoctorCreateForm()

    return render(request, 'admin_dashboard/doctor_form.html', {
        'form': form,
        'page_title': 'Add Doctor',
        'button_text': 'Add Doctor'
    })



@login_required(login_url='/login')
@admin_required
def doctor_edit(request, doctor_id):
    doctor = get_object_or_404(
        Doctors.objects.select_related('user', 'specialty', 'user__id_address'),
        pk=doctor_id
    )
    user = doctor.user
    address = user.id_address

    if request.method == 'POST':
        form = DoctorUpdateForm(request.POST, user_instance=user)
        if form.is_valid():
            # update address
            if address is None:
                address = Address.objects.create()
                user.id_address = address

            address.address_line = form.cleaned_data.get('address_line')
            address.city = form.cleaned_data.get('city')
            address.region = form.cleaned_data.get('region')
            address.code_postal = form.cleaned_data.get('code_postal')
            address.save()

            # update user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.gender = form.cleaned_data['gender']
            user.birthday = form.cleaned_data.get('birthday')
            user.is_doctor = form.cleaned_data.get('is_doctor', False)
            user.id_address = address
            user.save()

            # update doctor profile
            doctor.specialty = form.cleaned_data['specialty']
            doctor.bio = form.cleaned_data.get('bio', '')
            doctor.save()

            messages.success(request, "Doctor updated successfully.")
            return redirect('admin_doctor_list')
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'gender': user.gender,
            'birthday': user.birthday,
            'specialty': doctor.specialty,
            'bio': doctor.bio,
            'address_line': address.address_line if address else '',
            'city': address.city if address else '',
            'region': address.region if address else '',
            'code_postal': address.code_postal if address else '',
            'is_doctor': user.is_doctor,
        }
        form = DoctorUpdateForm(initial=initial_data, user_instance=user)

    return render(request, 'admin_dashboard/doctor_form.html', {
        'form': form,
        'page_title': 'Edit Doctor',
        'button_text': 'Update Doctor'
    })


@login_required(login_url='/login')
@admin_required
def doctor_delete(request, doctor_id):
    doctor = get_object_or_404(Doctors.objects.select_related('user'), pk=doctor_id)

    if request.method == 'POST':
        user = doctor.user
        doctor.delete()
        user.delete()
        messages.success(request, "Doctor deleted successfully.")
        return redirect('admin_doctor_list')

    return render(request, 'admin_dashboard/doctor_confirm_delete.html', {
        'doctor': doctor
    })






@staff_member_required(login_url='/login')
def patient_list(request):
    patients = Patients.objects.select_related("user", "user__id_address").all().order_by("user__first_name")
    return render(request, "admin_dashboard/patient_list.html", {
        "patients": patients
    })


@staff_member_required(login_url='/login')
def patient_detail(request, patient_id):
    patient = get_object_or_404(
        Patients.objects.select_related("user", "user__id_address"),
        pk=patient_id
    )

    appointments = Appointment.objects.filter(
        patient=patient
    ).select_related(
        "doctor__user", "status", "time"
    ).order_by("-start_date")

    return render(request, "admin_dashboard/patient_detail.html", {
        "patient": patient,
        "appointments": appointments
    })


@staff_member_required(login_url='/login')
def patient_delete(request, patient_id):
    patient = get_object_or_404(Patients, pk=patient_id)

    if request.method == "POST":
        patient.user.delete()   # delete user also because Patient is OneToOne with Users
        messages.success(request, "Patient deleted successfully.")
        return redirect("admin_patient_list")

    return render(request, "admin_dashboard/patient_delete.html", {
        "patient": patient
    })



@staff_member_required(login_url='/login')
def report_dashboard(request):
    today = date.today()

    start_of_week = today - timedelta(days=today.weekday())   # Monday
    end_of_week = start_of_week + timedelta(days=6)           # Sunday

    total_appointments = Appointment.objects.count()

    today_appointments = Appointment.objects.filter(
        start_date=today
    ).count()

    weekly_appointments = Appointment.objects.filter(
        start_date__range=(start_of_week, end_of_week)
    ).count()

    total_patients_today = Appointment.objects.filter(
        start_date=today
    ).values("patient").distinct().count()

    return render(request, "admin_dashboard/report_dashboard.html", {
        "total_appointments": total_appointments,
        "today_appointments": today_appointments,
        "weekly_appointments": weekly_appointments,
        "total_patients_today": total_patients_today,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
    })


@staff_member_required(login_url='/login')
def appointments_per_day_report(request):
    appointments_per_day = (
        Appointment.objects
        .values("start_date")
        .annotate(total=Count("pk"))
        .order_by("-start_date")
    )

    return render(request, "admin_dashboard/appointments_per_day.html", {
        "appointments_per_day": appointments_per_day
    })

@staff_member_required(login_url='/login')
def appointments_per_week_report(request):
    today = date.today()

    # current week: Monday -> Sunday
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # create all 7 days with default 0
    week_days = OrderedDict()
    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        week_days[current_day] = 0

    # get appointments of this week
    weekly_data = (
        Appointment.objects
        .filter(start_date__range=(start_of_week, end_of_week))
        .values("start_date")
        .annotate(total=Count("pk"))
        .order_by("start_date")
    )

    # fill counts into dictionary
    for item in weekly_data:
        week_days[item["start_date"]] = item["total"]

    return render(request, "admin_dashboard/appointments_per_week.html", {
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "week_days": week_days,
        "weekly_data": weekly_data,   # debug help
    })



@staff_member_required(login_url='/login')
def daily_patient_flow_report(request):
    patient_flow = (
        Appointment.objects
        .values("start_date")
        .annotate(total_patients=Count("patient", distinct=True))
        .order_by("-start_date")
    )

    return render(request, "admin_dashboard/daily_patient_flow.html", {
        "patient_flow": patient_flow
    })

