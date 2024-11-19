from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    text = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="questions")
    
    def __str__(self):
        return f"Question: {self.text[:50]}... - Subject: {self.subject.name}"

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer: {self.text[:50]}... - {'Correct' if self.is_correct else 'Incorrect'}"

    
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)  # Approval status for login
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name='staff')  # Course assigned to staff
    subjects = models.ManyToManyField(Subject, related_name='staff')  # Subjects assigned to staff

    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.approved else 'Pending Approval'}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)  # Approval status for login
    enrollment_number = models.CharField(max_length=100, unique=True)
    course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')  # Course selected by the student

    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.approved else 'Pending Approval'}"



