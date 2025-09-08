from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    

    USER_ROLE_CHOICES = [
       
        ('Branch Manager', 'Branch Manager'),
        ('HO Manager', 'HO Manager'),
        ('HO Audit', 'HO Audit'),
        ('Admin', 'Admin'),
    ]

    branch_name = models.CharField(blank=True,null=True)
    branch_code = models.CharField(blank=True,null=True)
    departments = models.ManyToManyField(Department, blank=True, related_name="users")

    user_role = models.CharField(
        max_length=50,
        choices=USER_ROLE_CHOICES,
        default='Branch Manager'
    )

    def __str__(self):
        return self.username









class BankMaster(models.Model):
    branch_code = models.CharField(max_length=20, unique=True)
    branch_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.branch_code} - {self.branch_name}"


from django.db import models
from django.conf import settings

class Observation(models.Model):


    PERIOD_CHOICES = [
        ("JANUARY", "JANUARY"),
        ("FEBRUARY", "FEBRUARY"),
        ("MARCH", "MARCH"),
        ("APRIL", "APRIL"),
        ("MAY", "MAY"),
        ("JUNE", "JUNE"),
        ("JULY", "JULY"),
        ("AUGUST", "AUGUST"),
        ("SEPTEMBER", "SEPTEMBER"),
        ("OCTOBER", "OCTOBER"),
        ("NOVEMBER", "NOVEMBER"),
        ("DECEMBER", "DECEMBER"),
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
        ('ANNUAL', 'ANNUAL'),
    ]

    AUDIT_CHOICES =[
        ('INTERNAL', 'INTERNAL'),
        ('CONCURRENT', 'CONCURRENT'),
    ]

    STATUS_CHOICES =[
        ('OPEN', 'OPEN'),
        ('CLOSED', 'CLOSED'),
    ]


    APPROVED_CHOICES = [
        ('YES', 'YES'),
    ]

    point = models.CharField()
    branch_code = models.CharField(max_length=50)
    audit_type = models.CharField(choices=AUDIT_CHOICES,default='INTERNAL')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    approved = models.CharField(max_length=10,choices=APPROVED_CHOICES,null=True,blank=True)
    department = models.CharField(max_length=150)
    category = models.TextField()
    checklist = models.TextField()
    auditors_remarks = models.TextField()
    risk_category = models.CharField(max_length=150)
    branch_remarks = models.TextField()
    ho_remarks = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    financial_year = models.CharField(max_length=9)  # e.g. "2024-2025"
    period = models.CharField(max_length=50,choices=PERIOD_CHOICES)        # e.g. "Q1", "Q2"

    email_recipients = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name="observation_emails",blank=True)

    created_at = models.DateTimeField(auto_now_add=True)  # auto timestamp
    updated_at = models.DateTimeField(auto_now=True)  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    updated_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_observations",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    


    def __str__(self):
        return f"{self.point} - {self.branch_code} ({self.status})"



class ObservationFile(models.Model):
    observation = models.ForeignKey('Observation', related_name='files', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=255)  # store original filename
    file_data = models.BinaryField()  # store actual file content in DB
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name




class AnnexureFile(models.Model):
    observation = models.ForeignKey('Observation', related_name='annexure_files', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=255)
    file_data = models.BinaryField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name




from django.db import models
from django.utils import timezone

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title


