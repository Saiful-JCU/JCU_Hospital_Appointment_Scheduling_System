from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Doctors, Patients, Address , Reste_token , Specialty, Contact
from doctors.models import DoctorSchedule, Blogs
from .helpers import send_email
import uuid

def home(request):
  doctors = Doctors.objects.select_related('user', 'specialty').all()
  blogs = Blogs.objects.filter(is_published=True).select_related('doctor', 'id_category').order_by('-posted_at')[:6]

  for doctor in doctors:
        doctor.has_slots = doctor.schedules.filter(is_available=True).exists()
  return render(request, "users/index.html", {'doctors': doctors, "blogs": blogs})


def blog(request):
    blogs = Blogs.objects.filter(is_published=True).select_related('doctor', 'id_category').order_by('-posted_at')
    return render(request, "users/blog.html", {'blogs': blogs})


def doctor_slots(request, doctor_id):
    doctor = Doctors.objects.prefetch_related("schedules").get(pk=doctor_id)
    slots = doctor.schedules.filter(is_available=True)

    return render(request, "users/doctor_slots.html", {
        "doctor": doctor,
        "slots": slots
    })

Users = get_user_model()


def register(request):
  specialities = Specialty.objects.all()
  if request.method == 'POST':
    user_status = request.POST.get('user_config')
    first_name = request.POST.get('user_firstname', '').strip()
    last_name = request.POST.get('user_lastname', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('conf_password', '')
    username = request.POST.get('user_id', '').strip()
    gender = request.POST.get('user_gender')
    birthday = request.POST.get('birthday')
    address_line = request.POST.get('address_line', '').strip()
    region = request.POST.get('region', '').strip()
    city = request.POST.get('city', '').strip()
    pincode = request.POST.get('pincode', '').strip()
    profile_pic = request.FILES.get('profile_pic')
    bio = request.POST.get('bio', '').strip()
    insurance = request.POST.get('insurance', '').strip()

    if user_status not in ['Doctor', 'Patient']:
      messages.error(request, 'Please choose either Doctor or Patient.')
    elif not first_name or not last_name or not email or not password or not confirm_password or not address_line or not region or not city or not pincode:
      messages.error(request, 'Please complete all required fields.')
    elif len(password) < 6:
      messages.error(request, 'Password must be at least 6 characters long.')
    elif password != confirm_password:
      messages.error(request, 'Passwords do not match.')
    elif Users.objects.filter(email__iexact=email).exists():
      messages.error(request, 'Email already exists. Please login or use a different email.')
    else:
      if not username:
        username = email.split('@')[0] if '@' in email else f"{first_name}{last_name}"[:50]
      if Users.objects.filter(username=username).exists():
        username = f"{username}{uuid.uuid4().hex[:6]}"

      if user_status == 'Doctor' and (not request.POST.get('Speciality') or not bio):
        messages.error(request, 'Doctors must select a specialty and provide a bio.')
      elif user_status == 'Patient' and not insurance:
        messages.error(request, 'Patients must provide an insurance provider or plan.')
      else:
        address = Address.objects.create(address_line=address_line, region=region, city=city, code_postal=pincode)

        user = Users.objects.create_user(
          first_name=first_name,
          last_name=last_name,
          profile_avatar=profile_pic,
          username=username,
          email=email,
          gender=gender,
          birthday=birthday,
          password=password,
          id_address=address,
          is_doctor=(user_status == 'Doctor')
        )

        if user_status == 'Doctor':
          specialty_name = Specialty.objects.get(name=request.POST.get('Speciality'))
          Doctors.objects.create(user=user, specialty=specialty_name, bio=bio)
        else:
          Patients.objects.create(user=user, insurance=insurance)

        messages.success(request, 'Your account has been successfully registered. Please login.', extra_tags='success')
        return redirect('login')

    return render(request, 'users/register.html', context={
          'specialities': specialities,
          'user_config': user_status,
          'user_firstname': first_name,
          'user_lastname': last_name,
          'user_id': username,
          'email': email,
          'user_gender': gender,
          'birthday': birthday,
          'address_line': address_line,
          'region': region,
          'city': city,
          'pincode': pincode,
          'bio': bio,
          'insurance': insurance,
      })

  return render(request, 'users/register.html' , {'specialities':specialities})


def login_view(request):
  next_url = request.GET.get('next', '') if request.method == 'GET' else request.POST.get('next', request.GET.get('next', ''))
  email = ''
  if request.method == 'POST':
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    if not email or not password:
      messages.error(request, 'Email and password are required.')
      return render(request, 'users/login.html', {'email': email, 'next': next_url})

    user = authenticate(request, email=email, password=password)

    if user is not None:
      login(request, user)
      if user.is_doctor:
        return redirect('doctor_dashboard')
      elif Patients.objects.filter(user=user).exists():
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
          return redirect(next_url)
        return redirect('patient_dashboard')
      else:
        messages.error(request, 'Your account is not linked to any user profile.')
    else:
      messages.error(request, 'Incorrect email or password')

    return render(request, 'users/login.html', {'email': email, 'next': next_url})
  
  return render(request, 'users/login.html', {'email': email, 'next': next_url})


def forgot_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = Users.objects.filter(email__iexact=email).first()
        if user:
            token = str(uuid.uuid4())
            reset, _ = Reste_token.objects.update_or_create(
                email=user.email,
                defaults={
                    'user': user,
                    'token': token,
                }
            )
            sent = send_email(user.email, token)
            if sent:
                return render(request, 'users/forgot.html', context={'send_email_succes': 1})
        else:
            return render(request, 'users/forgot.html', context={'errorlogin': 1})
    return render(request, 'users/forgot.html')

def reset_view(request,token):
    if request.method == 'POST':
        reste = Reste_token.objects.filter(token=token).first()
        if reste:
            password = request.POST.get('password')
            confirm_password = request.POST.get('conf_password')
            if len(password) < 6:
                messages.error(request, 'Password must be at least 6 characters long.')
                return render(request, 'users/reset.html', {'token': token})
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'users/reset.html', {'token': token})
            user = Users.objects.filter(email=reste.email).first()
            if user:
                user.set_password(password)
                user.save()
                reste.delete()
                return redirect('login')
            else:
                return render(request, 'users/reset.html', {'token': token, 'errorlogin': 1})
        messages.error(request, 'Invalid or expired reset token.')
        return render(request, 'users/reset.html', {'token': token})
    return render(request, 'users/reset.html', {'token': token})


@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('login')



# @login_required(login_url='/login')
def browse_doctors(request, doctor_id=None):

    # if request.user.is_doctor:
    #     messages.error(request, 'Only patients can book appointments.')
    #     return redirect('login')

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

  

    return render(request, "users/browse_doctors.html", {
        "doctors": doctors,
        "specialities": specialities,
        "filter_speciality": filter_speciality,
        "filter_doctor_name": filter_doctor_name,
        "filter_city": filter_city,
    })



def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if name and email and message:
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, "Message sent successfully!")
            return redirect("index")

        messages.error(request, "Please fill required fields.")

    return render(request, "users/contact.html")


