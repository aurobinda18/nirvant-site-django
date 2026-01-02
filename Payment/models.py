from django.db import models

class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_description = models.TextField()
    course_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course_name
