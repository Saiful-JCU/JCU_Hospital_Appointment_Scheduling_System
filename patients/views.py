from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime, date, timedelta
from django.urls import reverse
from django.db.models import Count
from users.models import Doctors, Specialty, Patients
from patients.models import Appointment, Time, Status
from doctors.models import ConsultationNote, DoctorSchedule

User = get_user_model()

@login_required(login_url='/login')
def patient_dashboard(request):
    if request.user.is_doctor:
        messages.error(request, "Only patients can access patient dashboard.")
        return redirect("doctor_dashboard")

    try:
        patient = Patients.objects.select_related("user", "user__id_address").get(user=request.user)
    except Patients.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect("login")

    # all appointments of this patient
    appointments = (
        Appointment.objects
        .filter(patient=patient)
        .select_related("doctor__user", "status", "time", "schedule")
        .order_by("-start_date")
    )

    # stats
    total_appointments = appointments.count()
    accepted_appointments = appointments.filter(status__status__iexact="Accepted").count()
    waited_appointments = appointments.filter(status__status__iexact="Waited").count()
    cancelled_appointments = appointments.filter(status__status__iexact="Cancelled").count()

    # today's appointments
    today_appointments = appointments.filter(start_date=date.today())[:6]

    # recent consultation notes for this patient
    consultation_notes = (
        ConsultationNote.objects
        .filter(patient=request.user)
        .select_related("doctor__user")
        .order_by("-created_at")[:5]
    )

    # chart data: appointments in current month grouped by date
    current_month = date.today().month
    monthly_appointments = (
        appointments.filter(start_date__month=current_month)
        .values("start_date")
        .annotate(count=Count("id"))
        .order_by("start_date")
    )

    chart_labels = [item["start_date"].strftime("%d %b") for item in monthly_appointments]
    chart_data = [item["count"] for item in monthly_appointments]

    context = {
        "patient": patient,
        "appointments": appointments,
        "today_appointments": today_appointments,
        "consultation_notes": consultation_notes,

        "total_appointments": total_appointments,
        "accepted_appointments": accepted_appointments,
        "waited_appointments": waited_appointments,
        "cancelled_appointments": cancelled_appointments,

        "chart_labels": chart_labels,
        "chart_data": chart_data,
    }

    return render(request, "patients/patient_dashboard.html", context)


@login_required(login_url='/login')
def my_appointments(request):
  app = Appointment.objects.filter(patient__user = request.user)
  
  filter_status = request.GET.get('filter_status')
  filter_date = request.GET.get('filter_date')
  filter_doctor_name = request.GET.get('filter_doctor_name')

  if filter_status and filter_status != 'All':
    app = app.filter(status__status=filter_status)

  if filter_date:
    app = app.filter(start_date=filter_date)

  if filter_doctor_name:
    app = app.filter(doctor__user__first_name__icontains=filter_doctor_name)

  return render(request, "patients/my_appointments.html", {
    'appointments': app,
    'filter_status': filter_status,
    'filter_date': filter_date,
    'filter_doctor_name': filter_doctor_name
  })


# @login_required(login_url='/login')
# def book_appointment(request, doctor_id=None):

#     if request.user.is_doctor:
#         messages.error(request, 'Only patients can book appointments.')
#         return redirect(f"{reverse('login')}?next={reverse('book_appointment')}")

#     specialities = Specialty.objects.all()
#     doctors = Doctors.objects.all()

#     filter_speciality = request.GET.get('filter_speciality')
#     filter_city = request.GET.get('filter_city')
#     filter_doctor_name = request.GET.get('filter_doctor_name')

#     if filter_speciality and filter_speciality != 'All':
#         doctors = doctors.filter(specialty__name=filter_speciality)

#     if filter_doctor_name:
#         doctors = doctors.filter(user__first_name__icontains=filter_doctor_name)

#     if filter_city:
#         doctors = doctors.filter(user__id_address__city__icontains=filter_city)

#     selected_doctor = None
#     slots = None

#     if doctor_id:
#         selected_doctor = Doctors.objects.prefetch_related("schedules").filter(pk=doctor_id).first()
#         if selected_doctor:
#             slots = selected_doctor.schedules.filter(is_available=True)

#     return render(request, "patients/book_appointment.html", {
#         'doctors': doctors,
#         'specialities': specialities,
#         'filter_speciality': filter_speciality,
#         'filter_doctor_name': filter_doctor_name,
#         'filter_city': filter_city,
#         'selected_doctor': selected_doctor,
#         'slots': slots,
#     })


@login_required(login_url='/login')
def book_appointment(request, doctor_id=None):

    if request.user.is_doctor:
        messages.error(request, 'Only patients can book appointments.')
        return redirect('login')

    specialities = Specialty.objects.all()

    filter_speciality = request.GET.get('filter_speciality')
    filter_city = request.GET.get('filter_city')
    filter_doctor_name = request.GET.get('filter_doctor_name')

    # base queryset
    doctors = Doctors.objects.select_related('user').prefetch_related('schedules')

    # filters
    if filter_speciality and filter_speciality != 'All':
        doctors = doctors.filter(specialty__name=filter_speciality)

    if filter_doctor_name:
        doctors = doctors.filter(user__first_name__icontains=filter_doctor_name)

    if filter_city:
        doctors = doctors.filter(user__id_address__city__icontains=filter_city)

  

    return render(request, "patients/book_appointment.html", {
        "doctors": doctors,
        "specialities": specialities,
        "filter_speciality": filter_speciality,
        "filter_doctor_name": filter_doctor_name,
        "filter_city": filter_city,
    })


def get_status_by_name(status_name):
    status, _ = Status.objects.get_or_create(status=status_name)
    return status

# @login_required(login_url='/login')
# def patient_confirm_book(request, doctor):
#   if request.user.is_doctor:
#     messages.error(request, 'Only patients can book appointments. Please login as a patient.')
#     return redirect(f"{reverse('login')}?next={reverse('book_appointment')}")

#   try:
#     doc = Doctors.objects.get(user__username=doctor)
#   except Doctors.DoesNotExist:
#     messages.error(request, 'Doctor not found. Please select another doctor.')
#     return redirect('book_appointment')

#   if request.method == 'POST':
#     date_str = request.POST.get('date')
#     summary = request.POST.get('summary', '').strip()
#     description = request.POST.get('description', '').strip()
#     time_value = request.POST.get('time')
#     patient = Patients.objects.get(user=request.user)

#     if not date_str or not summary or not time_value:
#       messages.error(request, 'Please provide a date, time, and summary for the appointment.')
#     else:
#       try:
#         appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
#       except ValueError:
#         appointment_date = None

#       if not appointment_date:
#         messages.error(request, 'The appointment date is invalid.')
#       elif appointment_date < date.today():
#         messages.error(request, 'The appointment date must be in the future.')
#       else:
#         try:
#           heure = Time.objects.get(time=time_value)
#         except Time.DoesNotExist:
#           heure = None
#           messages.error(request, 'The selected time slot is invalid.')

#         if heure:
#           existing_appointment = Appointment.objects.filter(
#               doctor=doc,
#               start_date=appointment_date,
#               time=heure
#           ).exists()

#           if existing_appointment:
#             messages.error(request, 'This slot is already booked. Please choose another date or time.')
#           else:
#             status = get_status_by_name('Waited')
#             Appointment.objects.create(
#               summary=summary,
#               description=description,
#               start_date=appointment_date,
#               time=heure,
#               doctor=doc,
#               patient=patient,
#               status=status
#             )
#             messages.success(request, 'Appointment booked successfully.')
#             return redirect('my_appointments')

#   times = Time.objects.all()
#   return render(request, 'patients/patient_confirm_book.html', {'times': times, 'doctor': doc})

@login_required(login_url='/login')
def patient_confirm_book(request, schedule_id):

    if request.user.is_doctor:
        messages.error( request, 'Only patients can book appointments.' )
        return redirect('home')

    patient = get_object_or_404( Patients, user=request.user )
    schedule = get_object_or_404( DoctorSchedule, pk=schedule_id, is_available=True )

    if request.method == 'POST':
        summary = request.POST.get( 'summary', '' ).strip()
        description = request.POST.get( 'description', '' ).strip()

        if not summary:
            messages.error( request, 'Summary is required.' )
        else:
            status = get_status_by_name('Waited')
            Appointment.objects.create(
                doctor=schedule.doctor,
                patient=patient,
                summary=summary,
                description=description,
                start_date=schedule.date,
                status=status,
            )

            schedule.is_available = False
            schedule.save()
            messages.success( request, 'Appointment booked successfully.' )
            return redirect( 'my_appointments' )
    return render( request, 'patients/patient_confirm_book.html', { 'schedule': schedule } )




@login_required(login_url='/login')
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)
    if request.method == 'POST':
        if appointment.status.status == 'Cancelled':
            messages.info(request, 'This appointment is already cancelled.')
        else:
            cancel_status = get_status_by_name('Cancelled')
            if appointment.start_date <= date.today():
                messages.error(request, 'Appointments on the same day cannot be cancelled here. Please contact support.')
            else:
                appointment.status = cancel_status
                appointment.save()
                messages.success(request, 'Appointment cancelled successfully.')
        return redirect('my_appointments')

    return render(request, 'patients/cancel_appointment.html', {'appointment': appointment})

@login_required(login_url='/login')
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)
    if appointment.status.status == 'Cancelled':
        messages.error(request, 'Cancelled appointments cannot be rescheduled.')
        return redirect('my_appointments')

    times = Time.objects.all()
    if request.method == 'POST':
        date_str = request.POST.get('date')
        time_value = request.POST.get('time')

        if not date_str or not time_value:
            messages.error(request, 'Please select a new date and time.')
        else:
            try:
                new_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                new_date = None

            if not new_date:
                messages.error(request, 'The selected date is invalid.')
            elif new_date < date.today():
                messages.error(request, 'The new date must be in the future.')
            else:
                try:
                    new_time = Time.objects.get(time=time_value)
                except Time.DoesNotExist:
                    new_time = None
                    messages.error(request, 'The selected time slot is invalid.')

                if new_time:
                    is_conflict = Appointment.objects.filter(
                        doctor=appointment.doctor,
                        start_date=new_date,
                        time=new_time
                    ).exclude(id=appointment.id).exists()

                    if is_conflict:
                        messages.error(request, 'The selected doctor already has an appointment in that slot.')
                    else:
                        appointment.start_date = new_date
                        appointment.time = new_time
                        appointment.status = get_status_by_name('Waited')
                        appointment.save()
                        messages.success(request, 'Appointment rescheduled successfully.')
                        return redirect('my_appointments')

    return render(request, 'patients/reschedule_appointment.html', {
        'appointment': appointment,
        'times': times,
    })


@login_required(login_url='/login')
def my_consultation_notes(request):
    if request.user.is_doctor:
        messages.error(request, "Only patients can view consultation notes.")
        return redirect("doctor_dashboard")  

    if not Patients.objects.filter(user=request.user).exists():
        raise PermissionDenied("You are not allowed to access patient notes.")
    return redirect("index") 

    notes = ConsultationNote.objects.filter( patient=request.user ).select_related("doctor", "doctor__user").order_by("-created_at")

    return render(request, "patients/my_consultation_notes.html", { "notes": notes })


@login_required(login_url='/login')
def consultation_note_detail(request, note_id):
    """
    Show a single consultation note only if it belongs to the logged-in patient.
    Prevents one patient from opening another patient's note by changing the URL.
    """
    if request.user.is_doctor:
        messages.error(request, "Only patients can view consultation notes.")
        return redirect("doctor_dashboard")  

    if not Patients.objects.filter(user=request.user).exists():
        raise PermissionDenied("You are not allowed to access patient notes.")

    note = get_object_or_404( ConsultationNote.objects.select_related("doctor", "doctor__user"), id=note_id, patient=request.user   )

    return render(request, "patients/consultation_note_detail.html", {
        "note": note
    })



