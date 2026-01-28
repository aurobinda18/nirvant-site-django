from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import json
from django.contrib.auth.models import User 

from .forms import ProfileForm

# Add these imports (keep existing ones)
from .models import (
    StudentProfile,
    Mentor,
    StudentProgress,
    SubjectProgress,
    TestScore,
    StudyLog,
    StudentGoal,
    # ADD THESE:
    Batch,
    TestSeries,
    StudentBatch,
    StudentTestSeries,
    PYQPDF,
    Notice
)

@login_required
def profile_view(request):
    # Get or create profile
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'attempt_year': 2025,
            'neet_exam_date': '2025-05-05',
            'batch_enrolled': 'NEET 2025 Batch A',
            'mentor_assigned': 'Dr. Sharma',
            'mentor_qualification': 'MBBS, AIIMS'
        }
    )
    
    # Get all mentors for dropdown - ADDED THIS
    mentors = Mentor.objects.all()
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    days_to_neet = profile.days_to_neet()
    
    context = {
        'profile': profile,
        'user': request.user,
        'form': form,
        'days_to_neet': days_to_neet,
        'mentors': mentors,  # ADDED THIS
    }
    return render(request, 'profile.html', context)

# ADD ONLY THIS NEW FUNCTION
@login_required
def mentor_view(request):
    return render(request, 'mentor.html')


@login_required
def mentor_dashboard(request):
    # Check if user is mentor
    if not hasattr(request.user, 'studentprofile') or request.user.studentprofile.user_type != 'mentor':
        messages.error(request, "Access denied. Mentor only.")
        return redirect('dashboard')
    
    # Get mentor's profile
    mentor_profile = request.user.studentprofile
    
    # FIX 1: Get mentor object from mentor field (not company_id)
    mentor_obj = mentor_profile.mentor
    
    if not mentor_obj:
        messages.error(request, "No mentor profile found. Please contact admin.")
        return redirect('dashboard')
    
    # FIX 2: Find students by mentor ForeignKey (NOT company_id)
    students = StudentProfile.objects.filter(
        mentor=mentor_obj,  # This is the ForeignKey to Mentor model
        user_type='student'
    )
    
    # Calculate statistics
    total_students = students.count()
    
    # Get batches count for this mentor
    batches_count = Batch.objects.filter(mentor=mentor_obj).count()
    
    # Count test series assigned
    tests_assigned = 0
    for student in students:
        tests_assigned += StudentTestSeries.objects.filter(student=student.user).count()
    
    # Calculate average progress
    avg_progress = 0
    progress_count = 0
    
    for student in students:
        try:
            progress = StudentProgress.objects.get(student=student.user)
            avg_progress += progress.overall_preparation
            progress_count += 1
        except StudentProgress.DoesNotExist:
            continue
    
    if progress_count > 0:
        avg_progress = avg_progress // progress_count
    
    context = {
        'mentor': mentor_profile,
        'mentor_obj': mentor_obj,  # Add mentor object
        'students': students,
        'total_students': total_students,
        'batches_count': batches_count,
        'tests_assigned': tests_assigned,
        'avg_progress': avg_progress,
    }
    return render(request, 'mentor_dashboard.html', context)

@login_required
def assign_students(request):
    # Only admin can access (you can change this later)
    if not request.user.is_staff:
        messages.error(request, "Admin only.")
        return redirect('dashboard')
    
    mentors = StudentProfile.objects.filter(user_type='mentor')
    students = StudentProfile.objects.filter(user_type='student')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        mentor_company_id = request.POST.get('mentor_company_id')
        
        try:
            student = StudentProfile.objects.get(id=student_id)
            student.mentor_company_id = mentor_company_id
            student.save()
            messages.success(request, f"Student assigned to mentor {mentor_company_id}")
        except:
            messages.error(request, "Error assigning student")
    
    context = {
        'mentors': mentors,
        'students': students,
    }
    return render(request, 'assign_students.html', context)

# Add this function in dashboard/views.py
@login_required
def progress_view(request):
    # Get user profile
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'attempt_year': 2025,
            'neet_exam_date': '2025-05-05',
            'batch_enrolled': 'NEET 2025 Batch A',
        }
    )
    
    # Get or create student progress
    student_progress, created_progress = StudentProgress.objects.get_or_create(
        student=request.user,
        defaults={
            'overall_preparation': 68,
            'total_study_hours': 32,
            'total_tests_taken': 2,
            'mentorship_streak': 15,
        }
    )
    
    # Get today's study log
    today = timezone.now().date()
    today_log, created_log = StudyLog.objects.get_or_create(
        student=request.user,
        date=today,
        defaults={'study_hours': 0, 'topics_completed': '[]'}
    )
    
    # Handle form submissions - SIMPLIFIED VERSION
    if request.method == 'POST':
        # FIX: Handle topic addition
        if 'add_topic' in request.POST:
            topic = request.POST.get('topic', '').strip()
            if topic:
                # Parse existing topics
                try:
                    topics = json.loads(today_log.topics_completed or '[]')
                except:
                    topics = []
                
                # Split by commas and add each topic
                new_topics = [t.strip() for t in topic.split(',') if t.strip()]
                for new_topic in new_topics:
                    if new_topic and new_topic not in topics:
                        topics.append(new_topic)
                
                today_log.topics_completed = json.dumps(topics)
                today_log.save()
                messages.success(request, f'Added {len(new_topics)} topic(s)!')
                return redirect('progress')
        
        # DELETE TOPICS
        elif 'remove_topic' in request.POST:
            topic_to_remove = request.POST.get('topic', '').strip()
            if topic_to_remove:
                # Parse existing topics
                try:
                    topics = json.loads(today_log.topics_completed or '[]')
                except:
                    topics = []
                
                # Remove the topic if it exists
                if topic_to_remove in topics:
                    topics.remove(topic_to_remove)
                    today_log.topics_completed = json.dumps(topics)
                    today_log.save()
                    messages.success(request, f'Removed topic: {topic_to_remove}')
                return redirect('progress')
        
        # KEEP ALL YOUR EXISTING CODE BELOW - DON'T CHANGE
        elif 'log_hours' in request.POST:
            hours = float(request.POST.get('study_hours', 0))
            if hours > 0:
                today_log.study_hours = hours
                today_log.save()
                
                # Update total hours
                student_progress.total_study_hours += int(hours)
                student_progress.save()
                
                messages.success(request, f'Study hours logged successfully!')
                return redirect('progress')
        
        elif 'add_test' in request.POST:
            subject = request.POST.get('subject')
            test_name = request.POST.get('test_name')
            score = int(request.POST.get('score', 0))
            max_marks = int(request.POST.get('max_marks', 100))
            date_taken = request.POST.get('date_taken')
            
            if subject and test_name and score and date_taken:
                percentage = round((score / max_marks) * 100, 2)
                
                TestScore.objects.create(
                    student=request.user,
                    subject=subject,
                    test_name=test_name,
                    score=score,
                    max_marks=max_marks,
                    date_taken=date_taken,
                    percentage=percentage
                )
                
                student_progress.total_tests_taken += 1
                student_progress.save()
                
                messages.success(request, 'Test score added successfully!')
                return redirect('progress')
        
        elif 'add_goal' in request.POST:
            goal_text = request.POST.get('goal_text')
            deadline = request.POST.get('deadline')
            
            if goal_text:
                StudentGoal.objects.create(
                    student=request.user,
                    goal_text=goal_text,
                    deadline=deadline if deadline else None
                )
                messages.success(request, 'Goal added successfully!')
                return redirect('progress')
        
        elif 'delete_goal' in request.POST:
            goal_id = request.POST.get('goal_id')
            try:
                goal = StudentGoal.objects.get(id=goal_id, student=request.user)
                goal.delete()
                messages.success(request, 'Goal deleted successfully!')
            except StudentGoal.DoesNotExist:
                messages.error(request, 'Goal not found!')
            return redirect('progress')
        
        elif 'delete_test' in request.POST:
            test_id = request.POST.get('test_id')
            try:
                test = TestScore.objects.get(id=test_id, student=request.user)
                test.delete()
                
                # Update test count
                student_progress.total_tests_taken = TestScore.objects.filter(student=request.user).count()
                student_progress.save()
                
                messages.success(request, 'Test score deleted successfully!')
            except TestScore.DoesNotExist:
                messages.error(request, 'Test score not found!')
            return redirect('progress')
        
        elif 'update_subject_target' in request.POST:
            subject_name = request.POST.get('subject')
            target = int(request.POST.get('target', 0))
            
            if subject_name and 0 <= target <= 100:
                subject_prog, created = SubjectProgress.objects.get_or_create(
                    student=request.user,
                    subject=subject_name,
                    defaults={
                        'progress_percentage': 0,
                        'needs_attention': '',
                        'weekly_target': target
                    }
                )
                subject_prog.weekly_target = target
                subject_prog.save()
                
                messages.success(request, f'Target updated for {subject_name}!')
            return redirect('progress')
    
    # Calculate days to NEET
    days_to_neet = profile.days_to_neet()
    
    # Get subject progress
    subjects_progress = []
    default_subjects = [
        {'name': 'Physics', 'progress': 72, 'needs_attention': 'Optics, Thermodynamics'},
        {'name': 'Chemistry', 'progress': 65, 'needs_attention': 'Organic Chemistry, Coordination Compounds'},
        {'name': 'Biology', 'progress': 75, 'needs_attention': 'Genetics, Ecology'},
    ]
    
    for subj in default_subjects:
        subject_prog, created = SubjectProgress.objects.get_or_create(
            student=request.user,
            subject=subj['name'],
            defaults={
                'progress_percentage': subj['progress'],
                'needs_attention': subj['needs_attention'],
                'weekly_target': subj['progress'] + 10
            }
        )
        
        subjects_progress.append({
            'name': subj['name'],
            'progress': subject_prog.progress_percentage,
            'needs_attention': subject_prog.needs_attention,
            'weekly_target': subject_prog.weekly_target,
            'id': subject_prog.id
        })
    
    # Get test scores
    test_scores = TestScore.objects.filter(student=request.user).order_by('-date_taken')[:10]
    
    # Get goals
    goals = StudentGoal.objects.filter(student=request.user, is_completed=False).order_by('-created_at')
    
    # Get all study logs for this week
    week_ago = today - timedelta(days=7)
    weekly_logs = StudyLog.objects.filter(
        student=request.user,
        date__gte=week_ago
    ).order_by('date')
    
    # Calculate weekly hours
    weekly_hours = [0, 0, 0, 0, 0, 0, 0]
    for log in weekly_logs:
        day_index = (log.date - week_ago).days
        if 0 <= day_index < 7:
            weekly_hours[day_index] = log.study_hours
    
    # Calculate total weekly hours
    weekly_hours_total = sum(weekly_hours)
    
    # Parse today's topics
    try:
        today_topics = json.loads(today_log.topics_completed or '[]')
    except:
        today_topics = []
    
    context = {
        'profile': profile,
        'days_to_neet': days_to_neet,
        'student_progress': student_progress,
        'today_log': today_log,
        'today_topics': today_topics,
        'subjects_progress': subjects_progress,
        'test_scores': test_scores,
        'goals': goals,
        'weekly_hours': weekly_hours,
        'weekly_hours_total': weekly_hours_total,
        'today': today.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'progress.html', context)

@login_required
def dashboard_view(request):
    # Get user profile
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'attempt_year': 2025,
            'neet_exam_date': '2025-05-05',
            'batch_enrolled': 'NEET 2025 Batch A',
        }
    )
    
    # Get active PYQ PDFs from database
    from .models import PYQPDF  # ADD THIS IMPORT
    pyq_pdfs = PYQPDF.objects.filter(is_active=True)
    
    # Calculate counts per subject
    physics_count = pyq_pdfs.filter(subject='Physics').count()
    chemistry_count = pyq_pdfs.filter(subject='Chemistry').count()
    biology_count = pyq_pdfs.filter(subject='Biology').count()
    
    # Calculate days to NEET
    days_to_neet = profile.days_to_neet()
    
    context = {
        'profile': profile,
        'user': request.user,
        'days_to_neet': days_to_neet,
        # Add these PYQ PDF variables
        'pyq_pdfs': pyq_pdfs,
        'physics_count': physics_count,
        'chemistry_count': chemistry_count,
        'biology_count': biology_count,
        'total_pyq': physics_count + chemistry_count + biology_count,
    }
    return render(request, 'dashboard.html', context)
@login_required
def studypack_view(request):
    # Get user profile
    from .models import StudentProfile, StudentBatch, StudentTestSeries
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'attempt_year': 2025,
            'neet_exam_date': '2025-05-05',
            'batch_enrolled': 'NEET 2025 Batch A',
        }
    )
    
    # Get student's batch enrollment
    student_batch = StudentBatch.objects.filter(
        student=request.user,
        is_active=True
    ).first()
    
    # Get student's test series enrollment
    test_series = StudentTestSeries.objects.filter(
        student=request.user,
        is_active=True
    ).first()
    
    # If no batch assigned, get from profile (for backward compatibility)
    if not student_batch and profile.batch_enrolled:
        from .models import Batch
        try:
            # Try to find a batch matching the profile's batch_enrolled
            default_batch = Batch.objects.filter(
                batch_name__icontains=profile.batch_enrolled
            ).first()
            
            if default_batch:
                student_batch = StudentBatch.objects.create(
                    student=request.user,
                    batch=default_batch,
                    is_active=True
                )
        except:
            pass
    
    context = {
        'profile': profile,
        'student_batch': student_batch,
        'test_series': test_series,
        'user': request.user,
    }
    
    return render(request, 'studypack.html', context)

@login_required
def assign_batch(request):
    # Check if user is mentor
    try:
        profile = request.user.studentprofile
        if profile.user_type != 'mentor':
            messages.error(request, "Access denied. Mentor only.")
            return redirect('dashboard')
    except:
        messages.error(request, "Please complete your profile first.")
        return redirect('profile')
    
    # Get mentor object
    mentor_obj = profile.mentor
    if not mentor_obj:
        messages.error(request, "No mentor profile found.")
        return redirect('mentor_dashboard')
    
    # Get mentor's students
    students = StudentProfile.objects.filter(
        mentor=mentor_obj,
        user_type='student'
    )
    
    # Get batches created by this mentor
    mentor_batches = Batch.objects.filter(mentor=mentor_obj, is_active=True)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # ACTION 1: Create New Batch
        if action == 'create_batch':
            batch_name = request.POST.get('batch_name')
            batch_code = request.POST.get('batch_code')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            max_students = request.POST.get('max_students', 50)
            description = request.POST.get('description', '')
            
            # Validation
            if not all([batch_name, batch_code, start_date, end_date]):
                messages.error(request, "Please fill all required fields.")
            elif Batch.objects.filter(batch_code=batch_code).exists():
                messages.error(request, f"Batch code '{batch_code}' already exists.")
            else:
                try:
                    # Create new batch
                    new_batch = Batch.objects.create(
                        batch_name=batch_name,
                        batch_code=batch_code,
                        start_date=start_date,
                        end_date=end_date,
                        mentor=mentor_obj,
                        max_students=int(max_students),
                        description=description,
                        is_active=True
                    )
                    
                    messages.success(request, f"Batch '{batch_name}' created successfully!")
                    
                    # Update mentor_batches to include the new one
                    mentor_batches = Batch.objects.filter(mentor=mentor_obj, is_active=True)
                    
                except Exception as e:
                    messages.error(request, f"Error creating batch: {str(e)}")
        
        # ACTION 2: Assign Batch to Students
        elif action == 'assign_batch':
            batch_id = request.POST.get('batch_id')
            student_ids = request.POST.get('student_ids', '')
            
            if not batch_id:
                messages.error(request, "Please select a batch.")
            elif not student_ids:
                messages.error(request, "Please select at least one student.")
            else:
                try:
                    batch = Batch.objects.get(id=batch_id, mentor=mentor_obj)
                    student_id_list = [id.strip() for id in student_ids.split(',') if id.strip()]
                    
                    assigned_count = 0
                    for student_id in student_id_list:
                        try:
                            student_profile = StudentProfile.objects.get(
                                user__id=student_id,
                                mentor=mentor_obj
                            )
                            
                            # Update student's batch
                            student_profile.batch_enrolled = batch.batch_name
                            student_profile.save()
                            
                            # Create or update StudentBatch record
                            StudentBatch.objects.update_or_create(
                                student=student_profile.user,
                                defaults={
                                    'batch': batch,
                                    'is_active': True
                                }
                            )
                            
                            # Update batch student count
                            batch.current_students = StudentBatch.objects.filter(batch=batch).count()
                            batch.save()
                            
                            assigned_count += 1
                            
                        except StudentProfile.DoesNotExist:
                            continue
                    
                    messages.success(request, f"Batch '{batch.batch_name}' assigned to {assigned_count} student(s) successfully!")
                    
                except Batch.DoesNotExist:
                    messages.error(request, "Invalid batch selected.")
                except Exception as e:
                    messages.error(request, f"Error assigning batch: {str(e)}")
    
    context = {
        'students': students,
        'mentor_batches': mentor_batches,
    }
    
    # Use the new professional template
    return render(request, 'assign_batch_pro.html', context)

@login_required
def manage_test_series(request):
    # Check if user is mentor
    try:
        profile = request.user.studentprofile
        if profile.user_type != 'mentor':
            messages.error(request, "Access denied. Mentor only.")
            return redirect('dashboard')
    except:
        messages.error(request, "Please complete your profile first.")
        return redirect('profile')
    
    # Get mentor's students
    students = StudentProfile.objects.filter(
        mentor=profile.mentor,
        user_type='student'
    )
    
    # Get all test series
    all_test_series = TestSeries.objects.filter(is_active=True)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # ACTION 1: Create New Test Series
        if action == 'create_series':
            series_name = request.POST.get('series_name')
            series_code = request.POST.get('series_code')
            total_tests = request.POST.get('total_tests')
            difficulty = request.POST.get('difficulty')
            subjects = request.POST.get('subjects')
            price = request.POST.get('price', 0.00)
            description = request.POST.get('description', '')
            
            # Validation
            if not all([series_name, series_code, total_tests, difficulty, subjects]):
                messages.error(request, "Please fill all required fields.")
            elif TestSeries.objects.filter(series_code=series_code).exists():
                messages.error(request, f"Test series code '{series_code}' already exists.")
            else:
                try:
                    # Create new test series
                    new_series = TestSeries.objects.create(
                        series_name=series_name,
                        series_code=series_code,
                        total_tests=int(total_tests),
                        difficulty=difficulty,
                        subjects=subjects,
                        price=float(price),
                        description=description,
                        is_active=True
                    )
                    
                    messages.success(request, f"Test series '{series_name}' created successfully!")
                    
                    # Update all_test_series to include the new one
                    all_test_series = TestSeries.objects.filter(is_active=True)
                    
                except Exception as e:
                    messages.error(request, f"Error creating test series: {str(e)}")
        
        # ACTION 2: Assign Test Series to Students
        elif action == 'assign_series':
            series_id = request.POST.get('series_id')
            student_ids = request.POST.get('student_ids', '')
            
            if not series_id:
                messages.error(request, "Please select a test series.")
            elif not student_ids:
                messages.error(request, "Please select at least one student.")
            else:
                try:
                    series = TestSeries.objects.get(id=series_id)
                    student_id_list = [id.strip() for id in student_ids.split(',') if id.strip()]
                    
                    assigned_count = 0
                    for student_id in student_id_list:
                        try:
                            student_profile = StudentProfile.objects.get(
                                user__id=student_id,
                                mentor=profile.mentor
                            )
                            
                            # Check if already enrolled
                            existing = StudentTestSeries.objects.filter(
                                student=student_profile.user,
                                test_series=series
                            ).first()
                            
                            if existing:
                                # Update if exists
                                existing.is_active = True
                                existing.save()
                            else:
                                # Create new enrollment
                                StudentTestSeries.objects.create(
                                    student=student_profile.user,
                                    test_series=series,
                                    is_active=True
                                )
                            
                            assigned_count += 1
                            
                        except StudentProfile.DoesNotExist:
                            continue
                    
                    messages.success(request, f"Test series '{series.series_name}' assigned to {assigned_count} student(s) successfully!")
                    
                except TestSeries.DoesNotExist:
                    messages.error(request, "Invalid test series selected.")
                except Exception as e:
                    messages.error(request, f"Error assigning test series: {str(e)}")
    
    context = {
        'students': students,
        'all_test_series': all_test_series,
    }
    
    return render(request, 'assign_test_series_pro.html', context)
@login_required
def upload_pyqs(request):
    # Check if user is mentor
    try:
        profile = request.user.studentprofile
        if profile.user_type != 'mentor':
            messages.error(request, "Access denied. Mentor only.")
            return redirect('dashboard')
    except:
        messages.error(request, "Please complete your profile first.")
        return redirect('profile')
    
    # Generate year range (2014 to current year)
    from datetime import datetime
    current_year = datetime.now().year
    year_range = list(range(2014, current_year + 1))
    year_range.reverse()  # Show latest years first
    
    # Get mentor's uploaded PDFs
    uploaded_pdfs = PYQPDF.objects.filter(
        uploaded_by=request.user,
        is_active=True
    ).order_by('-year', 'subject')
    
    # Calculate statistics
    total_pdfs = uploaded_pdfs.count()
    physics_count = uploaded_pdfs.filter(subject='Physics').count()
    chemistry_count = uploaded_pdfs.filter(subject='Chemistry').count()
    biology_count = uploaded_pdfs.filter(subject='Biology').count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # ACTION: Upload New PDF
        if action == 'upload_pdf':
            subject = request.POST.get('subject')
            year = request.POST.get('year')
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            pages = request.POST.get('pages', 1)
            questions_count = request.POST.get('questions', 0)
            pdf_file = request.FILES.get('pdf_file')
            
            # Validation
            if not all([subject, year, title, pdf_file]):
                messages.error(request, "Please fill all required fields.")
            elif not pdf_file.name.endswith('.pdf'):
                messages.error(request, "Only PDF files are allowed.")
            elif pdf_file.size > 50 * 1024 * 1024:  # 50MB limit
                messages.error(request, "File size exceeds 50MB limit.")
            else:
                try:
                    # Create new PYQPDF
                    new_pdf = PYQPDF.objects.create(
                        subject=subject,
                        year=year,
                        title=title,
                        description=description,
                        pdf_file=pdf_file,
                        pages=int(pages),
                        questions_count=int(questions_count),
                        uploaded_by=request.user,
                        is_active=True
                    )
                    
                    messages.success(request, f"PDF '{title}' uploaded successfully!")
                    
                    # Refresh the uploaded PDFs list
                    uploaded_pdfs = PYQPDF.objects.filter(
                        uploaded_by=request.user,
                        is_active=True
                    ).order_by('-year', 'subject')
                    
                    # Update statistics
                    total_pdfs = uploaded_pdfs.count()
                    physics_count = uploaded_pdfs.filter(subject='Physics').count()
                    chemistry_count = uploaded_pdfs.filter(subject='Chemistry').count()
                    biology_count = uploaded_pdfs.filter(subject='Biology').count()
                    
                except Exception as e:
                    messages.error(request, f"Error uploading PDF: {str(e)}")
    
    context = {
        'year_range': year_range,
        'uploaded_pdfs': uploaded_pdfs,
        'total_pdfs': total_pdfs,
        'physics_count': physics_count,
        'chemistry_count': chemistry_count,
        'biology_count': biology_count,
    }
    
    return render(request, 'upload_pyqs.html', context)

from django.http import FileResponse, Http404
import os

@login_required
def view_pdf(request, pdf_id):
    """View PDF in browser"""
    try:
        pdf = PYQPDF.objects.get(id=pdf_id, is_active=True)
        
        # Check if user has permission (student or mentor)
        if request.user.studentprofile.user_type == 'student':
            # Student can view any active PDF
            pass
        elif request.user.studentprofile.user_type == 'mentor':
            # Mentor can view their own PDFs
            if pdf.uploaded_by != request.user:
                raise Http404("PDF not found")
        else:
            raise Http404("Access denied")
        
        # Open and serve PDF file
        file_path = pdf.pdf_file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        else:
            raise Http404("PDF file not found")
            
    except PYQPDF.DoesNotExist:
        raise Http404("PDF not found")

@login_required
def download_pdf(request, pdf_id):
    """Download PDF file"""
    try:
        pdf = PYQPDF.objects.get(id=pdf_id, is_active=True)
        
        # Check if user has permission
        if request.user.studentprofile.user_type == 'student':
            # Student can download any active PDF
            pass
        elif request.user.studentprofile.user_type == 'mentor':
            # Mentor can download their own PDFs
            if pdf.uploaded_by != request.user:
                raise Http404("PDF not found")
        else:
            raise Http404("Access denied")
        
        # Serve file for download
        file_path = pdf.pdf_file.path
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{pdf.title}.pdf"'
            return response
        else:
            raise Http404("PDF file not found")
            
    except PYQPDF.DoesNotExist:
        raise Http404("PDF not found")
    
@login_required
def send_notices(request):
    # Check if user is mentor
    try:
        profile = request.user.studentprofile
        if profile.user_type != 'mentor':
            messages.error(request, "Access denied. Mentor only.")
            return redirect('dashboard')
    except:
        messages.error(request, "Please complete your profile first.")
        return redirect('profile')
    
    # Get mentor object
    mentor_obj = profile.mentor
    if not mentor_obj:
        messages.error(request, "No mentor profile found.")
        return redirect('mentor_dashboard')
    
    # Get mentor's students
    students = StudentProfile.objects.filter(
        mentor=mentor_obj,
        user_type='student'
    )
    
    # Get mentor's batches
    mentor_batches = Batch.objects.filter(mentor=mentor_obj, is_active=True)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send_notice':
            title = request.POST.get('title')
            message = request.POST.get('message')
            priority = request.POST.get('priority', 'medium')
            recipient_type = request.POST.get('recipient_type', 'all')
            specific_batch_id = request.POST.get('specific_batch')
            specific_student_id = request.POST.get('specific_student')
            
            # Validation
            if not all([title, message]):
                messages.error(request, "Please fill in title and message.")
            else:
                try:
                    # Create notice
                    notice = Notice.objects.create(
                        mentor=mentor_obj,
                        title=title,
                        message=message,
                        priority=priority,
                        recipient_type=recipient_type,
                        is_active=True
                    )
                    
                    # Set specific recipient if needed
                    if recipient_type == 'batch' and specific_batch_id:
                        try:
                            batch = Batch.objects.get(id=specific_batch_id, mentor=mentor_obj)
                            notice.specific_batch = batch
                            notice.save()
                        except Batch.DoesNotExist:
                            pass
                    
                    elif recipient_type == 'student' and specific_student_id:
                        try:
                            student = User.objects.get(id=specific_student_id)
                            notice.specific_student = student
                            notice.save()
                        except User.DoesNotExist:
                            pass
                    
                    # Determine recipients
                    recipients = []
                    if recipient_type == 'all':
                        recipients = [student.user for student in students]
                    elif recipient_type == 'batch' and notice.specific_batch:
                        # Get students in this batch
                        batch_students = StudentBatch.objects.filter(
                            batch=notice.specific_batch
                        ).select_related('student')
                        recipients = [student_batch.student for student_batch in batch_students]
                    elif recipient_type == 'student' and notice.specific_student:
                        recipients = [notice.specific_student]
                    
                    # Count affected students
                    affected_count = len(recipients)
                    
                    messages.success(request, f"Notice sent successfully to {affected_count} student(s)!")
                    
                    # Redirect to prevent form resubmission
                    return redirect('send_notices')
                    
                except Exception as e:
                    messages.error(request, f"Error sending notice: {str(e)}")
    
    context = {
        'students': students,
        'mentor_batches': mentor_batches,
        'total_students': students.count(),
    }
    
    return render(request, 'send_notices.html', context)