from django.db import models

class Course(models.Model):
    # PLAN TYPE
    PLAN_TYPE_CHOICES = [
        ('free_trial', 'Free Trial'),
        ('paid_trial', 'Paid Trial'),
        ('regular', 'Regular Plan'),
        ('neet_complete', 'NEET Complete Program'),
        ('other', 'Other'),
    ]
    
    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_TYPE_CHOICES,
        default='regular'
    )
    
    # BASIC INFO
    course_name = models.CharField(max_length=100)
    course_description = models.TextField()
    
    # DURATION
    duration_days = models.IntegerField(default=30)
    duration_text = models.CharField(max_length=50, default="30 days")
    
    # PRICING
    course_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.IntegerField(default=0)
    
    # BUTTON TEXT
    button_text = models.CharField(max_length=50, default="Enroll Now")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)  # For ordering courses

    def __str__(self):
        return f"{self.course_name} - {self.duration_text}"
    
    def calculate_discount_percentage(self):
        if self.original_price and self.original_price > 0:
            discount = ((self.original_price - self.course_price) / self.original_price) * 100
            return round(discount)
        return self.discount_percentage
    
    class Meta:
        ordering = ['display_order', 'created_at']