# users/tests/system_tests.py
# command - python manage.py runtestsall



from datetime import date, timedelta, time as dtime
from django.test import TestCase
from django.contrib.auth import get_user_model

from users.models import (
    Address,
    Contact,
    Reste_token,
    Specialty,
    Doctors,
    Patients,
)

from patients.models import (
    Time,
    Appointment,
    Status,
)

from doctors.models import (
    DoctorSchedule,
    ConsultationNote,
    Blogs,
    Comments,
    Category,
)

User = get_user_model()


class HospitalSystemTests(TestCase):
    """
    Whole-system tests for:
    - users app
    - patients app
    - doctors app
    """

    def setUp(self):
        # ---------------------------
        # Base shared objects
        # ---------------------------

        # Address
        self.address = Address.objects.create(
            address_line="123 Main Street",
            region="Dhaka",
            city="Dhaka",
            code_postal="1207"
        )

        # Main patient user
        self.user = User.objects.create_user(
            username="patient11",
            email="patient11@test.com",
            password="testpass123",
            first_name="Patient",
            last_name="One",
            gender="Male",
            id_address=self.address,
        )

        # Doctor user
        self.doctor_user = User.objects.create_user(
            username="doctor11",
            email="doctor11@test.com",
            password="doctorpass123",
            first_name="Doctor",
            last_name="One",
            gender="Male",
            is_doctor=True,
            id_address=self.address,
        )

        # Contact
        self.contact = Contact.objects.create(
            name="Test Contact",
            email="contact@test.com",
            subject="Test Subject",
            message="This is a test contact message."
        )

        # Specialty
        self.specialty, _ = Specialty.objects.get_or_create(
            name="Cardiology",
            defaults={"description": "Heart specialist"}
        )

        # Doctor profile
        self.doctor = Doctors.objects.create(
            user=self.doctor_user,
            specialty=self.specialty,
            bio="Experienced cardiologist"
        )

        # Patient profile
        self.patient = Patients.objects.create(
            user=self.user,
            insurance="Test Insurance"
        )

        # Status
        self.status = Status.objects.create(
            status="Pending"
        )

        # Time slot
        self.time_slot = Time.objects.create(
            time="10:00 AM"
        )

        # Category
        self.category = Category.objects.create(
            name="Health Tips"
        )

        # Doctor schedule
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            date=date.today() + timedelta(days=1),
            start_time=dtime(10, 0),
            end_time=dtime(11, 0),
            is_available=True
        )

        # Appointment
        self.appointment = Appointment.objects.create(
            schedule=self.schedule,
            doctor=self.doctor,
            patient=self.patient,
            summary="General Checkup",
            description="Routine health checkup",
            start_date=date.today() + timedelta(days=1),
            status=self.status,
            time=self.time_slot
        )

    # ==========================================================
    # USERS APP TESTS
    # ==========================================================

    def test_registration_success(self):
        """
        TC-001
        Positive test: valid user registration
        """
        new_user = User.objects.create_user(
            username="newuser1",
            email="newuser1@test.com",
            password="newpass123",
            first_name="New",
            last_name="User",
            gender="Male",
            id_address=self.address,
        )
        self.assertIsNotNone(new_user.pk)
        self.assertEqual(new_user.username, "newuser1")

    def test_invalid_login(self):
        """
        TC-002
        Negative test: wrong password should fail login
        """
        login_result = self.client.login(
            username="patient11",
            password="wrongpassword"
        )
        self.assertFalse(login_result)

    def test_create_address(self):
        """
        TC-003
        Positive test: address creation
        """
        self.assertIsNotNone(self.address.pk)
        self.assertEqual(self.address.city, "Dhaka")

    def test_create_contact(self):
        """
        TC-004
        Positive test: contact creation
        """
        self.assertIsNotNone(self.contact.pk)
        self.assertEqual(self.contact.email, "contact@test.com")

    def test_create_specialty(self):
        """
        TC-005
        Positive test: specialty creation
        """
        self.assertIsNotNone(self.specialty.pk)
        self.assertEqual(self.specialty.name, "Cardiology")

    def test_create_doctor(self):
        """
        TC-006
        Positive test: doctor profile creation
        """
        self.assertIsNotNone(self.doctor.pk)
        self.assertEqual(self.doctor.specialty.name, "Cardiology")

    def test_create_patient(self):
        """
        TC-007
        Positive test: patient profile creation
        """
        self.assertIsNotNone(self.patient.pk)
        self.assertEqual(self.patient.insurance, "Test Insurance")

    def test_create_reset_token(self):
        """
        Extra test if you want to include Reste_token in report later
        Positive test: reset token creation
        """
        reset = Reste_token.objects.create(
            user=self.user,
            email="reset@test.com",
            token="abc123token"
        )
        self.assertIsNotNone(reset.pk)
        self.assertEqual(reset.token, "abc123token")

    # ==========================================================
    # PATIENTS APP TESTS
    # ==========================================================

    def test_create_status(self):
        """
        TC-008
        Positive test: status creation
        """
        self.assertIsNotNone(self.status.pk)
        self.assertEqual(self.status.status, "Pending")

    def test_create_time(self):
        """
        TC-009
        Positive test: time creation
        """
        self.assertIsNotNone(self.time_slot.pk)
        self.assertEqual(self.time_slot.time, "10:00 AM")

    def test_create_appointment(self):
        """
        TC-010
        Positive test: appointment creation
        """
        self.assertIsNotNone(self.appointment.pk)
        self.assertEqual(self.appointment.summary, "General Checkup")
        self.assertEqual(self.appointment.doctor, self.doctor)
        self.assertEqual(self.appointment.patient, self.patient)

    def test_appointment_without_summary_should_fail(self):
        """
        Negative test:
        Appointment summary is required
        """
        with self.assertRaises(Exception):
            Appointment.objects.create(
                schedule=None,
                doctor=self.doctor,
                patient=self.patient,
                summary=None,
                description="Missing summary",
                start_date=date.today() + timedelta(days=2),
                status=self.status,
                time=self.time_slot
            )

    def test_duplicate_appointment_same_doctor_date_time_should_fail(self):
        """
        Boundary/constraint test:
        unique_together = (doctor, start_date, time)
        """
        with self.assertRaises(Exception):
            Appointment.objects.create(
                schedule=None,
                doctor=self.doctor,
                patient=self.patient,
                summary="Another Appointment",
                description="Should violate unique_together",
                start_date=self.appointment.start_date,
                status=self.status,
                time=self.time_slot
            )

    # ==========================================================
    # DOCTORS APP TESTS
    # ==========================================================

    def test_create_doctor_schedule(self):
        """
        TC-011
        Positive test: doctor schedule creation
        """
        self.assertIsNotNone(self.schedule.pk)
        self.assertEqual(self.schedule.doctor, self.doctor)
        self.assertTrue(self.schedule.is_available)

    def test_duplicate_doctor_schedule_same_date_time_should_fail(self):
        """
        Boundary/constraint test:
        DoctorSchedule unique_together = (doctor, date, start_time)
        """
        with self.assertRaises(Exception):
            DoctorSchedule.objects.create(
                doctor=self.doctor,
                date=self.schedule.date,
                start_time=self.schedule.start_time,
                end_time=dtime(12, 0),
                is_available=True
            )

    def test_create_consultation_note(self):
        """
        TC-012
        Positive test: consultation note creation
        """
        note = ConsultationNote.objects.create(
            doctor=self.doctor,
            patient=self.user,   # ConsultationNote.patient points to Users, not Patients
            title="Follow-up Advice",
            notes="Patient should take rest and drink water."
        )

        self.assertIsNotNone(note.pk)
        self.assertEqual(note.doctor, self.doctor)
        self.assertEqual(note.patient, self.user)

    def test_create_category(self):
        """
        TC-013
        Positive test: category creation
        """
        self.assertIsNotNone(self.category.pk)
        self.assertEqual(self.category.name, "Health Tips")

    def test_create_blog(self):
        """
        TC-014
        Positive test: blog creation
        """
        blog = Blogs.objects.create(
            title="Healthy Heart",
            description="Blog description",
            summary="Short summary",
            is_published=True,
            id_category=self.category,
            doctor=self.doctor
        )

        self.assertIsNotNone(blog.pk)
        self.assertEqual(blog.title, "Healthy Heart")
        self.assertEqual(blog.doctor, self.doctor)

    def test_create_comment(self):
        """
        TC-015
        Positive test: comment creation
        """
        blog = Blogs.objects.create(
            title="Healthy Heart",
            description="Blog description",
            summary="Short summary",
            is_published=True,
            id_category=self.category,
            doctor=self.doctor
        )

        comment = Comments.objects.create(
            content="Very helpful article.",
            user=self.user,
            blog=blog
        )

        self.assertIsNotNone(comment.pk)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.blog, blog)





