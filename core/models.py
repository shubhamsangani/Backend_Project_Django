from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

GROUP_CHOICES = (
    ('Breathing', 'Breathing'),
    ('Meditation', 'Meditation'),
    ('Relaxation', 'Relaxation'),
)

TYPE_CHOICES = (
    ('Audio', 'Audio'),
    ('Video', 'Video'),
    ('Article', 'Article'),
)

MOOD_CHOICES = (
    ('Calm', 'Calm'),
    ('Happy', 'Happy'),
    ('Excited', 'Excited'),
    ('Grateful', 'Grateful'),
    ('Angry', 'Angry'),
    ('Sad', 'Sad'),
    ('Confused', 'Confused'),
    ('Tired', 'Tired'),
    ('Neutral', 'Neutral')
)

class Psychiatrist(models.Model):
    full_name = models.CharField(max_length=255)
    profession = models.CharField(max_length=255)
    short_address = models.CharField(max_length=255)
    full_address = models.CharField(max_length=255)
    website_url = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    rating = models.FloatField()
    number_of_ratings = models.IntegerField()
    image = models.ImageField(upload_to="psych/")

    def __str__(self):
        return self.full_name


class FavoritePsychiatrist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    psychiatrists = models.ManyToManyField(Psychiatrist)

    def __str__(self):
        return self.user.email 


class Category(models.Model):
    category_name = models.CharField(max_length=255)
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, null=True)

    def __str__(self):
        return self.category_name
    

class SessionPart(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    audio = models.FileField(upload_to="audio/", blank=True, null=True)
    video = models.FileField(upload_to="video/", blank=True, null=True)
    image = models.ImageField(upload_to="psych/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    content_type = models.CharField(max_length=20, choices=TYPE_CHOICES, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    

class Session(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    group = models.CharField(max_length=20, choices=GROUP_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    image = models.ImageField(upload_to="psych/")
    segments = models.ManyToManyField(SessionPart, blank=True)
    audio = models.FileField(upload_to="audio/", blank=True, null=True)
    video = models.FileField(upload_to="video/", blank=True, null=True)
    mood = models.CharField(max_length=20, default="Neutral", choices=MOOD_CHOICES)
    description = models.TextField(blank=True, null=True)
    number_of_views = models.IntegerField(default=0)
    number_of_likes = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class RecentSessionView(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sessions = models.ManyToManyField(Session)

    def __str__(self):
        return self.user.email


class FavoriteSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sessions = models.ManyToManyField(Session)

    def __str__(self):
        return self.user.email


class FavoriteSessionPart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session_segments = models.ManyToManyField(SessionPart)

    def __str__(self):
        return self.user.email


class CompletedSessionDuration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hours = models.IntegerField(default=0)
    minutes = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email
    

class Faq(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question
    

class TermsAndConditons(models.Model):
    description = models.TextField()

    def __str__(self):
        return str(self.id)
    

class PrivacyPolicy(models.Model):
    description = models.TextField()

    def __str__(self):
        return str(self.id)
    

class UserMood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    mood = models.CharField(max_length=20, default="Neutral", choices=MOOD_CHOICES)

    def __str__(self):
        return self.user.email