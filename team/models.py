# models.py
from django.db import models

class TeamMember(models.Model):

    TEAM_CHOICES = [
        ('FOUNDERS', 'Founders'),
        ('SUPER_MENTORS', 'Super Mentors'),
        ('MENTORS', 'Mentors'),
    ]

    team_name = models.CharField(max_length=50, choices=TEAM_CHOICES)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team_photos/')

    def __str__(self):
        return self.name

