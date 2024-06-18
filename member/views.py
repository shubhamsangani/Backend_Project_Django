from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.utils.timezone import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
import os
import math
import datetime
import pytz
import random
import string

from .models import AuthToken, Otp, Profile, Event, Notification, CompletedTaskCount
from account.models import UserAccount
from .helpers import send_notifying_email
from .serializers import ProfileSerializer, UploadPicSerializer, EventSerializer


def generate_token():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class LoginView(APIView):
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = UserAccount.objects.filter(email=email).first()
        user = authenticate(email=email, password=password)

        token = generate_token()

        AuthToken.objects.create(
            user = user_obj,
            token = token
        )

        return Response({"token": token})
    

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


class RegisterView(APIView):
    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        user_obj = UserAccount(email=email, first_name=first_name, last_name=last_name)
        user_obj.set_password(password)
        user_obj.save()

        otp = generate_otp()
        Otp.objects.create(user=user_obj, verifying_otp=otp)
        
        subject = "Account Activation Required"
        email_template_name = "member/activation.html"
        c = {
            "otp": otp,
        }

        html_content = render_to_string(email_template_name, c)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        return Response({"status": "Ok"})


class ActivationView(APIView):
    def post(self, request):
        otp = request.POST.get('otp')
        print(otp)
        try:
            otp_obj = Otp.objects.filter(verifying_otp=otp).first()
            user_obj = UserAccount.objects.get(email=otp_obj.user.email)

            token = generate_token()

            AuthToken.objects.create(
                user = user_obj,
                token = token
            )

            return Response({"token": token})
        except:
            return Response({"status": "fail"})
    
    
class RecoverView(APIView):
    def post(self, request):
        email = request.POST.get('email')
        otp = generate_otp()

        user_obj = UserAccount.objects.filter(email=email).first()
        Otp.objects.create(user=user_obj, verifying_otp=otp)
        
        subject = "Password Reset Requested"
        email_template_name = "member/reset.html"
        c = {
            "otp": otp,
        }
        html_content = render_to_string(email_template_name, c)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        return Response({"status": "Ok"})
    

class ResetOtpView(APIView):
    def post(self, request):
        otp = request.POST.get('otp')
        return Response({"status": "Ok"})
    

class PasswordResetView(APIView):
    def post(self, request):
        password = request.POST.get('password')

        latest_otp = Otp.objects.all().order_by('-id').first()

        user_obj = UserAccount.objects.get(email=latest_otp.user.email)
        user_obj.set_password(password)
        user_obj.save()

        return Response({"status": "Ok"})
    

class ProfileInfo(APIView):    
    def post(self, request):
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        profile, created = Profile.objects.get_or_create(user=user_obj)

        return Response({
            "first_name": user_obj.first_name,
            "last_name": user_obj.last_name,
            "email": user_obj.email,
            "bio": profile.bio,
            "phone": profile.phone,
            "occupation": profile.occupation,
            "hobby": profile.hobby,
            "address": profile.address,
            "country": profile.country,
        })
            

class ProfileInformation(APIView):
    def post(self, request):
        bio = request.POST.get('bio')
        phone = request.POST.get('phone')
        occupation = request.POST.get('occupation')
        hobby = request.POST.get('hobby')
        address = request.POST.get('address')
        country = request.POST.get('country')
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        profile = Profile.objects.get(user__email=user_obj.email)

        if bio: 
            profile.bio = bio
        if phone:
            profile.phone = phone
        if occupation:
            profile.occupation = occupation
        if hobby:
            profile.hobby = hobby
        if address:
            profile.address = address
        if country:
            profile.country = country
        profile.save()

        return Response({"status": "Ok"})
    

class ProfilePic(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        profile_pic = request.FILES['picture']
        token = request.POST.get('token')
        
        auth_token = AuthToken.objects.filter(token=token).first()
        profile, created = Profile.objects.get_or_create(user__email=auth_token.user.email)

        # fss = FileSystemStorage()
        # file = fss.save(profile_pic.name, profile_pic)
        # file_url = fss.url(file)
        
        profile.picture = profile_pic
        profile.save()

        return Response({"status": "Ok"})
    

class EventListView(APIView):    
    def post(self, request):
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        events = Event.objects.filter(user__email=user_obj.email).order_by('start')
        
        data = []
        for event in events:
            start = event.start.astimezone(pytz.timezone('Asia/Dhaka'))
            start = start.strftime('%Y-%m-%d %H:%M:%S.%f')
            
            end = event.end.astimezone(pytz.timezone('Asia/Dhaka'))
            end = end.strftime('%Y-%m-%d %H:%M:%S.%f')

            data.append(
                {
                    "id": event.id,
                    "title": event.title,
                    "start": start,
                    "end": end,
                    "status": event.status,
                    "location": event.location,
                    "type": event.type,
                    "reminder": event.reminder,
                    "repetition": event.repetition,
                    "description": event.description,
                    "color": event.color,
                }
            )
        
        # event_serializer = EventSerializer(events)
        return Response(data)


class TodayEventListView(APIView):    
    def post(self, request):
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        raw_events = Event.objects.filter(user__email=user_obj.email).order_by('start')
        today = datetime.datetime.now()
        today_date = today.strftime('%d')

        collected_events = []
        for raw_event in raw_events:
            raw_start = raw_event.start.astimezone(pytz.timezone('Asia/Dhaka'))
            raw_start = raw_start.strftime('%d')

            if raw_start == today_date:
                collected_events.append(raw_event)

        data = []
        for event in collected_events:
            start = event.start.astimezone(pytz.timezone('Asia/Dhaka'))
            start = start.strftime('%Y-%m-%d %H:%M:%S.%f')
            
            end = event.end.astimezone(pytz.timezone('Asia/Dhaka'))
            end = end.strftime('%Y-%m-%d %H:%M:%S.%f')

            data.append(
                {
                    "id": event.id,
                    "title": event.title,
                    "start": start,
                    "end": end,
                    "status": event.status,
                    "location": event.location,
                    "type": event.type,
                    "reminder": event.reminder,
                    "repetition": event.repetition,
                    "description": event.description,
                    "color": event.color,
                }
            )
        
        return Response(data)


class EventCalendarView(APIView):    
    def post(self, request):
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        events = Event.objects.filter(user__email=user_obj.email).order_by('start')
        
        data = {}
        for event in events:
            startDate = event.start.astimezone(pytz.timezone('Asia/Dhaka'))
            startDate = startDate.strftime('%Y-%m-%d')
            
            start = event.start.astimezone(pytz.timezone('Asia/Dhaka'))
            start = start.strftime('%Y-%m-%d %H:%M:%S.%f')

            end = event.end.astimezone(pytz.timezone('Asia/Dhaka'))
            end = end.strftime('%Y-%m-%d %H:%M:%S.%f')

            data[startDate] = []
            data.update({
                startDate: [
                    {
                        "id": event.id,
                        "title": event.title,
                        "start": start,
                        "end": end
                    }
                ]
            })
        
        return Response(data)


class EventDayView(APIView):    
    def post(self, request):
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        selected_date_str = request.POST.get('selectedDate')    # 2023-10-26    (string)
        # selected_date_obj = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d')   # 2023-10-26 00:00:00   (datetime object)
        # selected_date_obj_tz = selected_date_obj.astimezone(pytz.timezone('Asia/Dhaka'))    # 2023-10-26 00:00:00+06:00   (datetime object with timezone)    

        events = Event.objects.filter(user__email=user_obj.email)

        dayEvents = []
        for event in events:
            start = event.start.astimezone(pytz.timezone('Asia/Dhaka'))   # 2023-10-26 22:00:00+06:00   (datetime object with timezone)
            end = event.end.astimezone(pytz.timezone('Asia/Dhaka'))
            
            startDate = start.strftime('%Y-%m-%d')   # 2023-10-26   (string)
            
            if startDate == selected_date_str:
                day_event = {
                    "id": event.id,
                    "title": event.title,
                    'startHour': start.strftime('%H'),   # 22   (string)
                    'start': start.strftime('%Y-%m-%d %H:%M:%S.%f'),    # 2023-10-26 22:00:00.000000    (string)
                    'end': end.strftime('%Y-%m-%d %H:%M:%S.%f'),
                    'color': event.color
                }
                dayEvents.append(day_event)
        
        return Response(dayEvents)
    

class EventDetailView(APIView):    
    def post(self, request):
        id = int(request.POST.get('id'))
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        event = Event.objects.get(id=id, user__email=user_obj.email)

        start = event.start.astimezone(pytz.timezone('Asia/Dhaka'))
        start = start.strftime('%Y-%m-%d %H:%M:%S.%f')
        
        end = event.end.astimezone(pytz.timezone('Asia/Dhaka'))
        end = end.strftime('%Y-%m-%d %H:%M:%S.%f')
        data = {
            "id": event.id,
            "title": event.title,
            "start": start,
            "end": end,
            "location": event.location,
            "type": event.type,
            "reminder": event.reminder,
            "repetition": event.repetition,
            "description": event.description
        }

        # event_serializer = EventSerializer(event)
        return Response(data)
    

class AddEventView(APIView):    
    def post(self, request):
        title = request.POST.get('title')
        start = request.POST.get('start')
        end = request.POST.get('end')
        location = request.POST.get('location')
        type = request.POST.get('type')
        reminder = request.POST.get('reminder')
        repetition = request.POST.get('repetition')
        color = request.POST.get('color')
        description = request.POST.get('description')
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)
        
        stripped_start = start.strip()
        if 'Z' in stripped_start:
            start = start.strip('Z')

        stripped_end = end.strip()
        if 'Z' in stripped_end:
            end = end.strip('Z')

        start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S.%f')
        start = start.astimezone(pytz.timezone('Asia/Dhaka'))

        end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S.%f')
        end = end.astimezone(pytz.timezone('Asia/Dhaka'))

        user = UserAccount.objects.get(email=user_obj.email)

        Event.objects.create(
            user=user,
            title=title,
            start=start,
            end=end,
            location=location,
            type=type,
            reminder=reminder,
            repetition=repetition,
            color=color,
            description=description
        )

        return Response({"status": "saved"})
    

class EditEventView(APIView):    
    def post(self, request):
        id = int(request.POST.get('id'))
        title = request.POST.get('title')
        start = request.POST.get('start')
        end = request.POST.get('end')
        location = request.POST.get('location')
        type = request.POST.get('type')
        reminder = request.POST.get('reminder')
        repetition = request.POST.get('repetition')
        description = request.POST.get('description')
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S.%f')
        start = start.astimezone(pytz.timezone('Asia/Dhaka'))

        end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S.%f')
        # end = end.astimezone(pytz.utc)
        end = end.astimezone(pytz.timezone('Asia/Dhaka'))

        event = Event.objects.get(id=id, user__email=user_obj.email)

        if title:
            event.title = title
        if start:
            event.start = start
        if end:
            event.end = end
        if location:
            event.location = location
        if type:
            event.type = type
        if reminder:
            event.reminder = reminder
        if repetition:
            event.repetition = repetition
        if description:
            event.description = description
        event.save()

        return Response({"status": "edited"})
    

class MarkEventView(APIView):    
    def post(self, request):
        id = int(request.POST.get('id'))
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        event = Event.objects.get(id=id, user__email=user_obj.email)
        event.status = "Completed"
        event.save()

        pallete, created = CompletedTaskCount.objects.get_or_create(user=user_obj)

        if created:
            pallete.numberOfTasks = 1
            pallete.save()
        else:
            pallete.numberOfTasks += 1
            pallete.save()

        return Response({"status": "Ok"})
    

class CompletedTasksCountView(APIView):    
    def post(self, request):
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        pallete, created = CompletedTaskCount.objects.get_or_create(user=user_obj)

        if created:
            number = 0
        else:
            number = pallete.numberOfTasks

        return Response({"number": number})
    

class DeleleEventView(APIView):    
    def post(self, request):
        id = int(request.POST.get('id'))
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        event = Event.objects.get(id=id, user__email=user_obj.email)
        event.delete()
        return Response({"status": "deleted"})
    

def notify_user():
    events = Event.objects.filter().order_by('start')
    
    if len(events) > 0:
        for event in events:
            time_diff = event.start - timezone.now()
            if time_diff.total_seconds() >= -60 and time_diff.total_seconds() <= 60:
                send_notifying_email(event)
                
                Notification.objects.create(
                    title = event.title,
                    desc = event.description,
                    start = event.start,
                )
                
                event.notified = True
                event.save()
                break 


class NotificationsView(APIView):
    def post(self, request):
        token = request.POST.get('token')

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        notifications = Notification.objects.filter(user__email=user_obj.email).order_by('-start')

        data = []
        if len(notifications) > 0:
            for notification in notifications:
                data.append({
                    "id": notification.id,
                    "title": notification.title,
                    "desc": notification.desc,
                    "start": notification.start
                })
            
        return Response(data)
    