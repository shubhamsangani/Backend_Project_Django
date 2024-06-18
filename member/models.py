from django.db import models
from django.conf import settings
from django.contrib.humanize.templatetags import humanize

User = settings.AUTH_USER_MODEL

TYPE_CHOICES = (
    ('Success', 'Success'), 
    ('Info', 'Info'), 
    ('Alert', 'Alert'), 
    ('Warning', 'Warning'), 
    ('Reminder', 'Reminder'), 
)

class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verifying_otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
    

class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    picture = models.ImageField(default="", null=True)
    bio = models.CharField(max_length=255, default="", null=True)
    phone = models.CharField(max_length=20, default="", null=True)
    occupation = models.CharField(max_length=255, default="", null=True)
    hobby = models.CharField(max_length=255, default="", blank=True, null=True)
    address = models.CharField(max_length=255, default="", null=True)
    country = models.CharField(max_length=255, default="", null=True)

    def __str__(self):
        return self.user.email


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.CharField(max_length=40, default='Not started')
    location = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=20, null=True)
    reminder = models.CharField(max_length=255)
    repetition = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)
    color = models.CharField(max_length=30, default='Green')

    def __str__(self):
        return self.title
    

class CompletedTaskCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    numberOfTasks = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    desc = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="Info")
    start = models.DateTimeField(auto_now_add=True)

    def get_date(self):
        return humanize.naturaltime(self.start)
    
    def __str__(self):
        return self.title 