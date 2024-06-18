from django.contrib import admin

from .models import Otp, AuthToken, Profile, Event, Notification, CompletedTaskCount


admin.site.register(Otp)
admin.site.register(AuthToken)
admin.site.register(Profile)
admin.site.register(Event)
admin.site.register(Notification)
admin.site.register(CompletedTaskCount)
