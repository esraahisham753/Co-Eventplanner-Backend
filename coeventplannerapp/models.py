from django.contrib.auth.models import AbstractUser
from django.db import models

STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

ROLE_CHOICES = [
        ('organizer', 'Organizer'),
        ('participant', 'Participant'),
    ]

class User(AbstractUser):
    image = models.ImageField(upload_to='user_images/', blank=True, null=True)
    job_title = models.CharField(max_length=64, blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Add related_name to avoid clash
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Add related_name to avoid clash
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=64)
    date = models.DateTimeField()

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tasks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")

class Team(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teams")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="teams")
    role = models.CharField(max_length=64, choices=ROLE_CHOICES, default='participant')
    invitation_status = models.BooleanField(default=False)

class BudgetItem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="budget_items")

class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")

class Message(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)