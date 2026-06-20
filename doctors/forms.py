from django import forms
from .models import DoctorSchedule


class DoctorScheduleForm(forms.ModelForm):

    class Meta:
        model = DoctorSchedule
        fields = [ "date", "start_time", "end_time", "is_available" ]

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date"}
            ),

            "start_time": forms.TimeInput(
                attrs={"type": "time"}
            ),

            "end_time": forms.TimeInput(
                attrs={"type": "time"}
            ),
        }









