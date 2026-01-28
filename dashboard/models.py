from django.db import models
from django.contrib.auth.models import User

class Mentor(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='mentor_photos/', blank=True, null=True)
    qualification = models.CharField(max_length=200)
    specialization = models.CharField(max_length=100, blank=True)
    # ADD THIS LINE
    company_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Add these TWO lines at the top of the class
    user_type = models.CharField(max_length=20, choices=[
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin')
    ], default='student')
    company_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Add this line to connect student to mentor
    mentor_company_id = models.CharField(max_length=50, blank=True, null=True)
    
    # NEET Information
    attempt_year = models.IntegerField(default=2025)
    neet_exam_date = models.DateField(default='2025-05-05')
    batch_enrolled = models.CharField(max_length=100, default="NEET 2025 Batch A")
    
    # Mentor connection
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Personal Details
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def days_to_neet(self):
        from datetime import date
        today = date.today()
        days_left = (self.neet_exam_date - today).days
        return max(days_left, 0)

    def get_mentor_notices(self):
        """Get all notices from student's mentor"""
        from .models import Notice
        
        if not self.mentor:
            return []
            
        notices = Notice.objects.filter(
            mentor=self.mentor,
            is_active=True
        ).order_by('-created_at')
        
        relevant_notices = []
        for notice in notices:
            if notice.recipient_type == 'all':
                relevant_notices.append(notice)
            elif notice.recipient_type == 'batch':
                if notice.specific_batch and self.batch_enrolled:
                    if notice.specific_batch.batch_name == self.batch_enrolled:
                        relevant_notices.append(notice)
            elif notice.recipient_type == 'student':
                if notice.specific_student == self.user:
                    relevant_notices.append(notice)
        
        return relevant_notices
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    # Add these models to your existing models.py

class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    overall_preparation = models.IntegerField(default=0)
    total_study_hours = models.IntegerField(default=0)
    total_tests_taken = models.IntegerField(default=0)
    mentorship_streak = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Student Progress"
    
    def __str__(self):
        return f"{self.student.username} - {self.overall_preparation}%"

class SubjectProgress(models.Model):
    SUBJECT_CHOICES = [
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_progress')
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    progress_percentage = models.IntegerField(default=0)
    needs_attention = models.TextField(blank=True, null=True)
    weekly_target = models.IntegerField(default=0)
    completed_topics = models.TextField(blank=True, null=True)  # JSON stored as text
    
    class Meta:
        unique_together = ['student', 'subject']
    
    def __str__(self):
        return f"{self.student.username} - {self.subject}: {self.progress_percentage}%"

class TestScore(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_scores')
    subject = models.CharField(max_length=100)
    test_name = models.CharField(max_length=200)
    score = models.IntegerField()
    max_marks = models.IntegerField()
    date_taken = models.DateField()
    percentage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_taken']
    
    def __str__(self):
        return f"{self.student.username} - {self.test_name}: {self.score}/{self.max_marks}"

class StudyLog(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_logs')
    date = models.DateField()
    study_hours = models.FloatField(default=0)
    topics_completed = models.TextField(blank=True, null=True)  # JSON stored as text
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.username} - {self.date}: {self.study_hours} hours"

class StudentGoal(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_text = models.TextField()
    deadline = models.DateField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.goal_text[:50]}"
    
# Add this to your models.py file
class PYQQuestion(models.Model):
    SUBJECT_CHOICES = [
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology'),
    ]
    
    YEAR_CHOICES = [(str(year), str(year)) for year in range(2014, 2026)]
    
    TOPIC_CHOICES = [
        # Physics Topics
        ('Mechanics', 'Mechanics'),
        ('Optics', 'Optics'),
        ('Thermodynamics', 'Thermodynamics'),
        ('Electromagnetism', 'Electromagnetism'),
        ('Modern Physics', 'Modern Physics'),
        ('Waves', 'Waves'),
        ('Electronics', 'Electronics'),
        
        # Chemistry Topics
        ('Organic Chemistry', 'Organic Chemistry'),
        ('Inorganic Chemistry', 'Inorganic Chemistry'),
        ('Physical Chemistry', 'Physical Chemistry'),
        ('Coordination Compounds', 'Coordination Compounds'),
        ('Biomolecules', 'Biomolecules'),
        ('Environmental Chemistry', 'Environmental Chemistry'),
        
        # Biology Topics
        ('Human Physiology', 'Human Physiology'),
        ('Plant Physiology', 'Plant Physiology'),
        ('Genetics', 'Genetics'),
        ('Ecology', 'Ecology'),
        ('Cell Biology', 'Cell Biology'),
        ('Biotechnology', 'Biotechnology'),
        ('Reproduction', 'Reproduction'),
    ]
    
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    year = models.CharField(max_length=4, choices=YEAR_CHOICES)
    topic = models.CharField(max_length=100, choices=TOPIC_CHOICES)
    question_number = models.IntegerField()
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ])
    explanation = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=20, choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ], default='Medium')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year', 'subject', 'question_number']
    
    def __str__(self):
        return f"{self.subject} {self.year} - Q{self.question_number}"
    

class PYQPDF(models.Model):
    SUBJECT_CHOICES = [
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology'),
    ]
    
    YEAR_CHOICES = [(str(year), str(year)) for year in range(2014, 2026)]
    
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    year = models.CharField(max_length=4, choices=YEAR_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='pyq_pdfs/')
    pages = models.IntegerField(default=1)
    questions_count = models.IntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_pdfs')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-year', 'subject']
        verbose_name = "PYQ PDF"
        verbose_name_plural = "PYQ PDFs"
    
    def __str__(self):
        return f"{self.subject} {self.year} - {self.title}"
    
    def file_size(self):
        if self.pdf_file:
            size_bytes = self.pdf_file.size
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes/1024:.1f} KB"
            else:
                return f"{size_bytes/(1024*1024):.1f} MB"
        return "0 B"
    
class Batch(models.Model):
    batch_name = models.CharField(max_length=200)
    batch_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='batches')
    max_students = models.IntegerField(default=100)
    current_students = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.batch_name} ({self.batch_code})"
    
    def is_full(self):
        return self.current_students >= self.max_students

class TestSeries(models.Model):
    series_name = models.CharField(max_length=200)
    series_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    total_tests = models.IntegerField(default=0)
    subjects = models.CharField(max_length=200, default="Physics, Chemistry, Biology")
    difficulty = models.CharField(max_length=50, choices=[
        ('Easy', 'Easy'),
        ('Moderate', 'Moderate'),
        ('Hard', 'Hard'),
        ('NEET Level', 'NEET Level'),
    ], default='NEET Level')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.series_name} ({self.series_code})"

class StudentBatch(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolled_batches')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'batch']
    
    def __str__(self):
        return f"{self.student.username} - {self.batch.batch_name}"

class StudentTestSeries(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolled_test_series')
    test_series = models.ForeignKey(TestSeries, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_date = models.DateField(auto_now_add=True)
    tests_completed = models.IntegerField(default=0)
    overall_score = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'test_series']
    
    def __str__(self):
        return f"{self.student.username} - {self.test_series.series_name}"
    
class Notice(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    RECIPIENT_CHOICES = [
        ('all', 'All Students'),
        ('batch', 'Specific Batch'),
        ('student', 'Specific Student'),
    ]
    
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='sent_notices')
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='all')
    
    # For specific recipients
    specific_batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='batch_notices')
    specific_student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_notices')
    
    # Track reads
    read_by = models.ManyToManyField(User, blank=True, related_name='read_notices')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.mentor.name}"
    
    def mark_as_read(self, user):
        """Mark notice as read by a user"""
        if user not in self.read_by.all():
            self.read_by.add(user)
    
    def is_read_by(self, user):
        """Check if notice is read by user"""
        return self.read_by.filter(id=user.id).exists()
def get_notices(self):
    """Get all notices for this student"""
    from .models import Notice
    
    notices = Notice.objects.filter(is_active=True)
    student_notices = []
    
    for notice in notices:
        if notice.recipient_type == 'all':
            student_notices.append(notice)
        elif notice.recipient_type == 'batch' and self.batch_enrolled:
            # Check if student is in the batch
            if notice.specific_batch and self.batch_enrolled == notice.specific_batch.batch_name:
                student_notices.append(notice)
        elif notice.recipient_type == 'student':
            if notice.specific_student == self.user:
                student_notices.append(notice)
    
    return student_notices

def get_unread_notices_count(self):
    """Count unread notices"""
    return len([n for n in self.get_notices() if not n.is_read_by(self.user)])