from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Appointment


def build_appointment_message(appointment):
    patient_name = appointment.patient.user.get_full_name() or appointment.patient.user.username
    doctor_name = appointment.doctor.user.get_full_name() or appointment.doctor.user.username
    appointment_date = appointment.start_date.strftime('%Y-%m-%d') if appointment.start_date else 'N/A'
    appointment_time = appointment.time.time if appointment.time else 'N/A'
    status = appointment.status.status if appointment.status else 'N/A'

    specialty = appointment.doctor.specialty.name if appointment.doctor and appointment.doctor.specialty else 'N/A'

    return (
        f"Hello,\n\n"
        f"Your appointment has been booked successfully. Here are the details:\n\n"
        f"Patient: {patient_name}\n"
        f"Patient email: {appointment.patient.user.email}\n"
        f"Doctor: Dr. {doctor_name}\n"
        f"Doctor email: {appointment.doctor.user.email}\n"
        f"Specialty: {specialty}\n"
        f"Date: {appointment_date}\n"
        f"Time: {appointment_time}\n"
        f"Status: {status}\n\n"
        f"Summary:\n{appointment.summary}\n\n"
        f"Description:\n{appointment.description}\n\n"
        f"If you have any questions, please reply to this email or contact hospital management at {settings.HOSPITAL_MANAGEMENT_EMAIL}.\n\n"
        f"Thank you,\n"
        f"JCU Hospital Appointment System"
    )


@receiver(post_save, sender=Appointment)
def send_appointment_notifications(sender, instance, created, **kwargs):
    if not created:
        return

    patient_email = instance.patient.user.email if instance.patient and instance.patient.user else None
    doctor_email = instance.doctor.user.email if instance.doctor and instance.doctor.user else None
    management_email = getattr(settings, 'HOSPITAL_MANAGEMENT_EMAIL', None)

    if not patient_email or not doctor_email or not management_email:
        return

    subject = f"Appointment Confirmed: {instance.summary}"
    message = build_appointment_message(instance)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)

    send_mail(subject, message, from_email, [patient_email], fail_silently=False)
    send_mail(subject, message, from_email, [doctor_email], fail_silently=False)
    send_mail(subject, message, from_email, [management_email], fail_silently=False)
