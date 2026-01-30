from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from dashboard.models import MentorProfile


class Call(models.Model):
    CALL_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('academic', 'Academic'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('missed_student', 'Missed by Student'),
        ('missed_mentor', 'Missed by Mentor'),
        ('rescheduled', 'Rescheduled'),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_calls'
    )

    mentor = models.ForeignKey(
        MentorProfile,
        on_delete=models.CASCADE,
        related_name='mentor_calls'
    )

    call_type = models.CharField(
        max_length=20,
        choices=CALL_TYPE_CHOICES
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.call_type} - {self.start_time}"


class MentorScheduleConfig(models.Model):
    mentor = models.OneToOneField(
        MentorProfile,
        on_delete=models.CASCADE,
        related_name='schedule_config'
    )

    weekday_start = models.TimeField()
    weekday_end = models.TimeField()

    sunday_morning_start = models.TimeField(null=True, blank=True)
    sunday_morning_end = models.TimeField(null=True, blank=True)

    sunday_evening_start = models.TimeField(null=True, blank=True)
    sunday_evening_end = models.TimeField(null=True, blank=True)

    dinner_start = models.TimeField(null=True, blank=True)
    dinner_end = models.TimeField(null=True, blank=True)

    gap_minutes = models.IntegerField(default=5)

    def __str__(self):
        return f"Schedule for {self.mentor}"
