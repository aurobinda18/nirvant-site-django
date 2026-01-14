from django.shortcuts import render
from Payment.models import Course  # Import your Course model

def courses_view(request):
    # Get only active courses, ordered by display_order
    courses = Course.objects.filter(is_active=True).order_by('display_order', 'created_at')
    
    context = {
        'courses': courses
    }
    return render(request, 'courses.html', context)