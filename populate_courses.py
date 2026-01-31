"""
Script to populate Course model with the pricing plans data.
Run this script to add/update pricing plans in the database.

Usage: python populate_courses.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nirvant.settings')
django.setup()

from Payment.models import Course

# Pricing Plans Data
pricing_plans = [
    {
        "id": 1,
        "plan_type": "free_trial",
        "course_name": "Free Trial Plan",
        "duration_text": "3 days",
        "duration_days": 3,
        "course_price": 0,
        "original_price": 0,
        "discount_percentage": 0,
        "button_text": "Start Free Trial",
        "display_order": 1,
        "course_description": "Try our mentorship program for free with 3 days access to all features."
    },
    {
        "id": 2,
        "plan_type": "paid_trial",
        "course_name": "Paid Trial Plan",
        "duration_text": "7 days",
        "duration_days": 7,
        "course_price": 150,
        "original_price": 200,
        "discount_percentage": 25,
        "button_text": "Enroll Now",
        "display_order": 2,
        "course_description": "Experience our complete mentorship program for a week at a discounted rate."
    },
    {
        "id": 3,
        "plan_type": "regular",
        "course_name": "Monthly Plan",
        "duration_text": "30 days",
        "duration_days": 30,
        "course_price": 600,
        "original_price": 800,
        "discount_percentage": 25,
        "button_text": "Enroll Now",
        "display_order": 3,
        "course_description": "One month of personalized NEET mentorship and study guidance."
    },
    {
        "id": 4,
        "plan_type": "regular",
        "course_name": "45 Days Plan",
        "duration_text": "45 days",
        "duration_days": 45,
        "course_price": 900,
        "original_price": 1200,
        "discount_percentage": 25,
        "button_text": "Enroll Now",
        "display_order": 4,
        "course_description": "Extended mentorship program for intensive NEET preparation."
    },
    {
        "id": 5,
        "plan_type": "regular",
        "course_name": "3 Months Plan",
        "duration_text": "90 days",
        "duration_days": 90,
        "course_price": 1800,
        "original_price": 2400,
        "discount_percentage": 25,
        "button_text": "Enroll Now",
        "display_order": 5,
        "course_description": "Complete 3-month mentorship program with comprehensive coverage."
    },
    {
        "id": 6,
        "plan_type": "neet_complete",
        "course_name": "NEET 2026 Complete",
        "duration_text": "NEET 2026",
        "duration_days": 365,
        "course_price": 3500,
        "original_price": 5000,
        "discount_percentage": 30,
        "button_text": "Enroll Now",
        "display_order": 6,
        "course_description": "Complete NEET 2026 preparation with personalized mentorship until exam day."
    }
]

def populate_courses():
    """Create or update course pricing plans."""
    print("=" * 60)
    print("POPULATING COURSE PRICING PLANS")
    print("=" * 60)
    
    for plan_data in pricing_plans:
        plan_id = plan_data.pop('id')
        
        # Check if course already exists
        course, created = Course.objects.update_or_create(
            id=plan_id,
            defaults=plan_data
        )
        
        if created:
            print(f"✓ Created: {course.course_name} ({course.duration_text})")
        else:
            print(f"✓ Updated: {course.course_name} ({course.duration_text})")
    
    print("=" * 60)
    print(f"Total courses in database: {Course.objects.count()}")
    print("=" * 60)
    print("\n✨ Course pricing plans populated successfully!")
    
    # Display summary
    print("\n📊 PRICING SUMMARY:")
    print("-" * 60)
    for course in Course.objects.all().order_by('display_order'):
        print(f"{course.duration_text:15} | ₹{course.course_price:>6} | {course.plan_type}")
    print("-" * 60)

if __name__ == "__main__":
    populate_courses()
