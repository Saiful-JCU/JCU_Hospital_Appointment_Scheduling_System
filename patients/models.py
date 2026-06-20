from email.policy import default

from django.db import models
from users.models import Patients ,Doctors
from doctors.models import DoctorSchedule

class Time(models.Model):
    time = models.CharField(max_length=10)
    class Meta:
        verbose_name = "Time"
        verbose_name_plural = "Times"
    def __str__(self):
        return self.time
    
class Status(models.Model):
    status =  models.CharField(max_length=20) 
    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"
    def __str__(self):
        return self.status

class Appointment(models.Model):
    schedule = models.OneToOneField( DoctorSchedule, on_delete=models.CASCADE, null=True, blank=True )
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    summary = models.TextField()
    description = models.TextField()
    start_date = models.DateField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        unique_together = ('doctor', 'start_date', 'time')

    def __str__(self):
        return self.summary
    

