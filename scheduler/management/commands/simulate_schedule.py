from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta, time

from scheduler.services.weekly_scheduler import schedule_week
from scheduler.models import Call, MentorScheduleConfig
from dashboard.models import MentorProfile

def get_next_monday():
    today = timezone.now().date()
    days_ahead = 0 - today.weekday()  # Monday = 0
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


class Command(BaseCommand):
    help = "Simulate weekly scheduling with dummy data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting scheduling simulation...")


        # 1. Create dummy students
        students = []
        for i in range(1, 141):
            user, created = User.objects.get_or_create(
                username=f"dummy_student_{i}",
                defaults={"email": f"student{i}@example.com"}
            )
            students.append({"user_id": user.id})

        self.stdout.write("Created dummy students")


        # 2. Create dummy mentors
        mentors = []

        # Normal mentors
        for i in range(1, 8):
            user, _ = User.objects.get_or_create(
                username=f"dummy_mentor_{i}",
                defaults={"email": f"mentor{i}@example.com"}
            )

            from dashboard.models import StudentProfile
            student_profile, _ = StudentProfile.objects.get_or_create(user=user)
            student_profile.user_type = 'mentor'
            student_profile.save()

            mentor_profile, _ = MentorProfile.objects.get_or_create(
                user=user
            )

            MentorScheduleConfig.objects.get_or_create(
                mentor=mentor_profile,
                defaults={
                    "weekday_start": time(19, 0),
                    "weekday_end": time(0, 0),
                    "sunday_morning_start": time(10, 0),
                    "sunday_morning_end": time(12, 0),
                    "sunday_evening_start": time(19, 0),
                    "sunday_evening_end": time(0, 0),
                    "dinner_start": time(21, 0),
                    "dinner_end": time(22, 0),
                    "gap_minutes": 5,
                }
            )

            mentors.append({
                "mentor_id": mentor_profile.id,
                "type": "normal",
                "weekday_window": ("19:00", "24:00"),
                "sunday_windows": [("10:00", "12:00"), ("19:00", "24:00")],
                "breaks": [("21:00", "22:00")],
                "gap_minutes": 5,
            })


        # Academic mentors
        for i in range(8, 11):
            user, _ = User.objects.get_or_create(
                username=f"dummy_academic_{i}",
                defaults={"email": f"academic{i}@example.com"}
            )

            from dashboard.models import StudentProfile
            student_profile, _ = StudentProfile.objects.get_or_create(user=user)
            student_profile.user_type = 'mentor'
            student_profile.save()

            mentor_profile, _ = MentorProfile.objects.get_or_create(
                user=user
            )

            MentorScheduleConfig.objects.get_or_create(
                mentor=mentor_profile,
                defaults={
                    "weekday_start": time(19, 0),
                    "weekday_end": time(0, 0),
                    "sunday_morning_start": time(10, 0),
                    "sunday_morning_end": time(12, 0),
                    "sunday_evening_start": time(19, 0),
                    "sunday_evening_end": time(0, 0),
                    "dinner_start": time(21, 0),
                    "dinner_end": time(22, 0),
                    "gap_minutes": 5,
                }
            )

            mentors.append({
                "mentor_id": mentor_profile.id,
                "type": "academic",
                "weekday_window": ("19:00", "24:00"),
                "sunday_windows": [("10:00", "12:00"), ("19:00", "24:00")],
                "breaks": [("21:00", "22:00")],
                "gap_minutes": 5,
            })


        # 3. Run scheduler brain
        calls = schedule_week(students, mentors)


        week_start = timezone.now().date() + timedelta(days=1)

        day_to_offset = {
            "mon": 0,
            "tue": 1,
            "wed": 2,
            "thu": 3,
            "fri": 4,
            "sat": 5,
            "sun": 6,
        }

        # 4. Save calls to database
        Call.objects.all().delete()  # clean previous simulation

        def build_datetime(base_date, time_str):
            hour, minute = map(int, time_str.split(":"))
            if hour == 24 and minute == 0:
                base_date = base_date + timedelta(days=1)
                hour = 0
            return timezone.make_aware(
                datetime.combine(
                    base_date,
                    datetime.min.time().replace(
                        hour=hour,
                        minute=minute
                    )
                )
            )

        for c in calls:
            day_offset = day_to_offset[c["day"]]
            call_date = week_start + timedelta(days=day_offset)

            start_datetime = build_datetime(call_date, c["start"])
            end_datetime = build_datetime(call_date, c["end"])

            Call.objects.create(
                student_id=c["student"],
                mentor_id=c["mentor"],
                call_type=c["type"],
                start_time=start_datetime,
                end_time=end_datetime,
                status="scheduled"
            )

        self.stdout.write(f"Simulation complete. {len(calls)} calls created.")
