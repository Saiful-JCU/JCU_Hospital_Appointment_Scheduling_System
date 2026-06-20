from django.contrib import admin
from .models import Users, Contact, Address, Doctors, Patients, Specialty


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id_address", "address_line", "city", "region", "code_postal")


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "email", "first_name", "last_name", "gender", "is_doctor", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_doctor", "gender", "is_active")


@admin.register(Doctors)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ("user", "specialty", "get_email", "get_full_name")
    list_filter = ("specialty",)

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = "Full Name"


@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = ("user", "insurance", "get_email", "get_full_name")

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = "Full Name"


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "subject", "created_at")
    search_fields = ("name", "email", "subject")
    list_filter = ("created_at",)