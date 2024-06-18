from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (Psychiatrist, FavoritePsychiatrist, CompletedSessionDuration, Category, SessionPart, Session, FavoriteSession, FavoriteSessionPart, RecentSessionView,
                    Faq, TermsAndConditons, PrivacyPolicy, UserMood)
from .serializers import SessionSerializer, CatSerializer, FaqSerializer
from member.models import AuthToken, Profile, CompletedTaskCount, Event
from account.models import UserAccount
import pytz
import math
from datetime import datetime, timedelta


class RecommendedListSessionsView(APIView):    
    def post(self, request):
        token = request.POST.get('token') 
        
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_session, created = FavoriteSession.objects.get_or_create(user=user_obj)
        favs = fav_session.sessions.all()

        dur, createdDur = CompletedSessionDuration.objects.get_or_create(user=user_obj)
        if createdDur:
            hours = 0
            minutes = 0
        else:
            hours = dur.hours
            minutes = dur.minutes
        
        sessions = Session.objects.all().order_by('-id')

        a_list = []
        for a in favs:
            a_list.append(a.id)

        b_list = []
        for b in sessions:
            b_list.append(b.id)

        loved_session_pks = []
        neutral_session_pks = []
        for c in b_list:
            if c in a_list:
                loved_session_pks.append(c)
            else:
                neutral_session_pks.append(c)

        sessionList = []

        if len(loved_session_pks) > 0:
            for loved_session_pk in loved_session_pks:
                x = Session.objects.filter(id=loved_session_pk).first()
                sessionList.append({
                    "id": x.id,
                    "title": x.title,
                    "subtitle": x.subtitle,
                    "cat_name": x.category.category_name,
                    "segments_count": x.segments.count(),
                    "content_type": x.content_type,
                    "image": x.image.url,
                    "liked": True
                })

        if len(neutral_session_pks) > 0:
            for neutral_session_pk in neutral_session_pks:
                y = Session.objects.filter(id=neutral_session_pk).first()
                sessionList.append({
                    "id": y.id,
                    "title": y.title,
                    "subtitle": y.subtitle,
                    "cat_name": y.category.category_name,
                    "segments_count": y.segments.count(),
                    "content_type": y.content_type,
                    "image": y.image.url,
                    "liked": False
                })

        return Response([{
            "sessionList": sessionList,
            "hours": hours,
            "minutes": minutes,
        }])


class MainHomeView(APIView):    
    def post(self, request):
        token = request.POST.get('token') 
        
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_session, created = FavoriteSession.objects.get_or_create(user=user_obj)
        favs = fav_session.sessions.all()
        
        user_mood_obj, created = UserMood.objects.get_or_create(user=user_obj)
        
        if user_mood_obj.mood == 'Neutral':
            sessions = Session.objects.all().order_by('-id')
        else:
            sessions = Session.objects.filter(mood=user_mood_obj.mood).order_by('-id')
            if len(sessions) == 0:
                sessions = Session.objects.all().order_by('-id')
        
        a_list = []
        for a in favs:
            a_list.append(a.id)

        b_list = []
        for b in sessions:
            b_list.append(b.id)

        loved_session_pks = []
        neutral_session_pks = []
        for c in b_list:
            if c in a_list:
                loved_session_pks.append(c)
            else:
                neutral_session_pks.append(c)

        sessionList = []

        if len(loved_session_pks) > 0:
            for loved_session_pk in loved_session_pks:
                x = Session.objects.filter(id=loved_session_pk).first()
                sessionList.append({
                    "id": x.id,
                    "title": x.title,
                    "subtitle": x.subtitle,
                    "cat_name": x.category.category_name,
                    "segments_count": x.segments.count(),
                    "content_type": x.content_type,
                    "image": x.image.url,
                    "liked": True
                })

        if len(neutral_session_pks) > 0:
            for neutral_session_pk in neutral_session_pks:
                y = Session.objects.filter(id=neutral_session_pk).first()
                sessionList.append({
                    "id": y.id,
                    "title": y.title,
                    "subtitle": y.subtitle,
                    "cat_name": y.category.category_name,
                    "segments_count": y.segments.count(),
                    "content_type": y.content_type,
                    "image": y.image.url,
                    "liked": False
                })

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

        profile_obj, created = Profile.objects.get_or_create(user=user_obj)
        
        if profile_obj.profile_picture == '':
            pic = "empty"
        else:
            pic = profile_obj.profile_picture.url

        profile = {
            "firstName": user_obj.first_name,
            "lastName": user_obj.last_name,
            "picture": pic
        }
                
        return Response([{
            "sessionList": sessionList,
            "data": data,
            "profile": profile
        }])


class FavoriteSessionsView(APIView):    
    def post(self, request):
        token = request.POST.get('token')   
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_panel, created = FavoriteSession.objects.get_or_create(user=user_obj)
        favs = fav_panel.sessions.all()

        sessionList = []
        if len(favs) > 0:
            for fav in favs:
                sessionList.append({
                    "id": fav.id,
                    "title": fav.title,
                    "subtitle": fav.subtitle,
                    "cat_name": fav.category.category_name,
                    "segments_count": fav.segments.count(),
                    "content_type": fav.content_type,
                    "image": fav.image.url,
                    "liked": True
                })

        fav_part_panel, created_part = FavoriteSessionPart.objects.get_or_create(user=user_obj)
        fav_segments = fav_part_panel.session_segments.all()

        if len(fav_segments) > 0:
            for f in fav_segments:
                sessionList.append({
                    "id": f.id,
                    "title": f.title,
                    "subtitle": f.subtitle,
                    "cat_name": f.category.category_name,
                    "segments_count": 0,
                    "content_type": f.content_type,
                    "image": f.image.url,
                    "liked": True
                })
        
        return Response(sessionList)


class ListSessionsView(APIView):    
    def post(self, request):
        token = request.POST.get('token') 
        group = request.POST.get('group') 
        
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)
        
        fav_session, created = FavoriteSession.objects.get_or_create(user=user_obj)
        
        favs = fav_session.sessions.all()
        a_list = []
        for a in favs:
            a_list.append(a.id)

        sessions = Session.objects.filter(group=group)
        b_list = []
        for b in sessions:
            b_list.append(b.id)

        loved_session_pks = []
        neutral_session_pks = []
        for c in b_list:
            if c in a_list:
                loved_session_pks.append(c)
            else:
                neutral_session_pks.append(c)

        sessionList = []

        if len(loved_session_pks) > 0:
            for loved_session_pk in loved_session_pks:
                x = Session.objects.filter(id=loved_session_pk).first()
                sessionList.append({
                    "id": x.id,
                    "title": x.title,
                    "subtitle": x.subtitle,
                    "cat_name": x.category.category_name,
                    "segments_count": x.segments.count(),
                    "content_type": x.content_type,
                    "image": x.image.url,
                    "liked": True
                })

        if len(neutral_session_pks) > 0:
            for neutral_session_pk in neutral_session_pks:
                y = Session.objects.filter(id=neutral_session_pk).first()
                sessionList.append({
                    "id": y.id,
                    "title": y.title,
                    "subtitle": y.subtitle,
                    "cat_name": y.category.category_name,
                    "segments_count": y.segments.count(),
                    "content_type": y.content_type,
                    "image": y.image.url,
                    "liked": False
                })

        cats = Category.objects.all()
        cats_serializer = CatSerializer(cats, many=True)
        
        catSess = [{
            "sessionList": sessionList,
            "cats": cats_serializer.data
        }]

        return Response(catSess)
    

class HomeProfileView(APIView):   
    def post(self, request):
        token = request.POST.get('token') 
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_session_pallete, created = FavoriteSession.objects.get_or_create(user=user_obj)
        fav_sessions = fav_session_pallete.sessions.all()
        f_list = []
        if len(f_list) > 0:
            for f in fav_sessions:
                f_list.append(f.id)
            
        recent_session_pallete, created = RecentSessionView.objects.get_or_create(user=user_obj)
        recent_sessions = recent_session_pallete.sessions.all()
        
        r_list = []
        if len(recent_sessions) > 0:
            for r in recent_sessions:
                r_list.append(r.id)

        loved_session_pks = []
        neutral_session_pks = []
        if len(r_list) > 0:
            for c in r_list:
                if c in f_list:
                    loved_session_pks.append(c)
                else:
                    neutral_session_pks.append(c)

        sessionList = []
        if len(loved_session_pks) > 0:
            for loved_session_pk in loved_session_pks:
                x = Session.objects.filter(id=loved_session_pk).first()
                sessionList.append({
                    "id": x.id,
                    "title": x.title,
                    "subtitle": x.subtitle,
                    "cat_name": x.category.category_name,
                    "segments_count": x.segments.count(),
                    "content_type": x.content_type,
                    "image": x.image.url,
                    "liked": True
                })

        if len(neutral_session_pks) > 0:
            for neutral_session_pk in neutral_session_pks:
                y = Session.objects.filter(id=neutral_session_pk).first()
                sessionList.append({
                    "id": y.id,
                    "title": y.title,
                    "subtitle": y.subtitle,
                    "cat_name": y.category.category_name,
                    "segments_count": y.segments.count(),
                    "content_type": y.content_type,
                    "image": y.image.url,
                    "liked": False
                })

        profile_obj, created = Profile.objects.get_or_create(user=user_obj)
        
        if profile_obj.profile_picture == '':
            pic = "empty"
        else:
            pic = profile_obj.profile_picture.url

        profile = {
            "firstName": user_obj.first_name,
            "lastName": user_obj.last_name,
            "picture": pic
        }

        completed_task_count, created = CompletedTaskCount.objects.get_or_create(user=user_obj)
        number = completed_task_count.numberOfTasks
        
        res = [{
            "sessionList": sessionList,
            "profile": profile,
            "completedTaskCount": number
        }]

        return Response(res)


class CategorizedSessionsView(APIView):    
    def post(self, request):
        cat_id = int(request.POST.get('catId'))   
        token = request.POST.get('token') 

        sessions = Session.objects.filter(category__id=cat_id)
        
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_session, created = FavoriteSession.objects.get_or_create(user=user_obj)

        favs = fav_session.sessions.all()
        a_list = []
        for a in favs:
            a_list.append(a.id)

        b_list = []
        for b in sessions:
            b_list.append(b.id)

        loved_session_pks = []
        neutral_session_pks = []
        for c in b_list:
            if c in a_list:
                loved_session_pks.append(c)
            else:
                neutral_session_pks.append(c)

        sessionList = []

        if len(loved_session_pks) > 0:
            for loved_session_pk in loved_session_pks:
                x = Session.objects.filter(id=loved_session_pk).first()
                sessionList.append({
                    "id": x.id,
                    "title": x.title,
                    "subtitle": x.subtitle,
                    "cat_name": x.category.category_name,
                    "segments_count": x.segments.count(),
                    "content_type": x.content_type,
                    "image": x.image.url,
                    "liked": True
                })

        if len(neutral_session_pks) > 0:
            for neutral_session_pk in neutral_session_pks:
                y = Session.objects.filter(id=neutral_session_pk).first()
                sessionList.append({
                    "id": y.id,
                    "title": y.title,
                    "subtitle": y.subtitle,
                    "cat_name": y.category.category_name,
                    "segments_count": y.segments.count(),
                    "content_type": y.content_type,
                    "image": y.image.url,
                    "liked": False
                })

        return Response(sessionList)
    

class SearchedSessionsView(APIView):    
    def post(self, request):
        q = request.POST.get('q')   
        token = request.POST.get('token') 

        sessions = Session.objects.filter(title__icontains=q)
        
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_session, created = FavoriteSession.objects.get_or_create(user=user_obj)
        
        favs = fav_session.sessions.all()
        a_list = []
        for a in favs:
            a_list.append(a.id)

        b_list = []
        for b in sessions:
            b_list.append(b.id)

        loved_session_pks = []
        neutral_session_pks = []
        for c in b_list:
            if c in a_list:
                loved_session_pks.append(c)
            else:
                neutral_session_pks.append(c)

        sessionList = []

        if len(loved_session_pks) > 0:
            for loved_session_pk in loved_session_pks:
                x = Session.objects.filter(id=loved_session_pk).first()
                sessionList.append({
                    "id": x.id,
                    "title": x.title,
                    "subtitle": x.subtitle,
                    "cat_name": x.category.category_name,
                    "segments_count": x.segments.count(),
                    "content_type": x.content_type,
                    "image": x.image.url,
                    "liked": True
                })

        if len(neutral_session_pks) > 0:
            for neutral_session_pk in neutral_session_pks:
                y = Session.objects.filter(id=neutral_session_pk).first()
                sessionList.append({
                    "id": y.id,
                    "title": y.title,
                    "subtitle": y.subtitle,
                    "cat_name": y.category.category_name,
                    "segments_count": y.segments.count(),
                    "content_type": y.content_type,
                    "image": y.image.url,
                    "liked": False
                })

        return Response(sessionList)


class SingleSessionView(APIView):    
    def post(self, request):
        session_id = request.POST.get('session_id')   
        token = request.POST.get('token') 

        session = Session.objects.filter(id=session_id).first()
        
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)
        
        fav_session, created = FavoriteSession.objects.get_or_create(user=user_obj)
        favs = fav_session.sessions.all()
        
        session_liked = False
        if len(favs) > 0:
            for fav in favs:
                if session_id == fav.id:
                    session_liked = True
                    break

        segs = session.segments.all()
        
        fav_session_part_panel, created = FavoriteSessionPart.objects.get_or_create(user=user_obj)
        fav_segs = fav_session_part_panel.session_segments.all()

        a_list = []
        for a in fav_segs:
            a_list.append(a.id)

        b_list = []
        for b in segs:
            b_list.append(b.id)

        loved_session_pks = []
        neutral_session_pks = []
        for c in b_list:
            if c in a_list:
                loved_session_pks.append(c)
            else:
                neutral_session_pks.append(c)

        segmentList = []

        if len(loved_session_pks) > 0:
            for loved_session_pk in loved_session_pks:
                x = SessionPart.objects.filter(id=loved_session_pk).first()
                segmentList.append({
                    "id": x.id,
                    "title": x.title,
                    "subtitle": x.subtitle,
                    "liked": True
                })

        if len(neutral_session_pks) > 0:
            for neutral_session_pk in neutral_session_pks:
                y = SessionPart.objects.filter(id=neutral_session_pk).first()
                segmentList.append({
                    "id": y.id,
                    "title": y.title,
                    "subtitle": y.subtitle,
                    "liked": False
                })

        return Response([{
            "id": session.id,
            "title": session.title,
            "subtitle": session.subtitle,
            "liked": session_liked,
            "content_type": session.content_type,
            "segment_count": len(segmentList),
            "segments": segmentList
        }])


class ContentView(APIView):    
    def post(self, request):
        is_portion = request.POST.get('is_portion')
        id = int(request.POST.get('id')) 
        content_type = request.POST.get('type')
        
        if is_portion == 'yes':
            part = SessionPart.objects.filter(id=id).first()

            if content_type == "Article":
                wordNum = len(part.description.split())
                readTime = math.ceil(wordNum / 220)

                card = {
                    "title": part.title,
                    "subtitle": part.subtitle,
                    "audio": "",
                    "video": "",
                    "image": part.image.url,
                    "desc": part.description,
                    "wordNum": wordNum,
                    "readTime": readTime
                }
            elif content_type == "Audio":
                card = {
                    "title": part.title,
                    "subtitle": part.subtitle,
                    "audio": part.audio.url,
                    "video": "",
                    "image": part.image.url,
                    "desc": "",
                    "wordNum": 0,
                    "readTime": 0
                }
            else:            
                card = {
                    "title": part.title,
                    "subtitle": part.subtitle,
                    "audio": "",
                    "video": part.video.url,
                    "image": part.image.url,
                    "desc": "",
                    "wordNum": 0,
                    "readTime": 0
                }
        else:                       
            session = Session.objects.filter(id=id).first()
            
            if content_type == "Article":
                wordNum = len(session.description.split())
                readTime = math.ceil(wordNum / 220)

                card = {
                    "title": session.title,
                    "subtitle": session.subtitle,
                    "audio": "",
                    "video": "",
                    "image": session.image.url,
                    "desc": session.description,
                    "wordNum": wordNum,
                    "readTime": readTime
                }
            elif content_type == "Audio":
                card = {
                    "title": session.title,
                    "subtitle": session.subtitle,
                    "audio": session.audio.url,
                    "video": "",
                    "image": session.image.url,
                    "desc": "",
                    "wordNum": 0,
                    "readTime": 0
                }
            else:            
                card = {
                    "title": session.title,
                    "subtitle": session.subtitle,
                    "audio": "",
                    "video": session.video.url,
                    "image": session.image.url,
                    "desc": "",
                    "wordNum": 0,
                    "readTime": 0
                }

        return Response(card)


class AddDurationView(APIView):    
    def post(self, request):
        token = request.POST.get('token') 
        dur = request.POST.get('dur')

        t = datetime.strptime(dur, "%H:%M:%S.%f")
        hours=t.hour
        minutes=t.minute
        seconds=t.second

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        duration_panel, created = CompletedSessionDuration.objects.get_or_create(user=user_obj)

        if not created:
            if minutes == 0 and seconds > 0:
                duration_panel.minutes += 1
                duration_panel.save()
            else:
                duration_panel.hours += hours
                duration_panel.minutes += minutes
                duration_panel.save()

        return Response({"status": "Ok"})


class AddLikingView(APIView):    
    def post(self, request):
        is_portion = request.POST.get('is_portion') 
        session_id = int(request.POST.get('id'))
        token = request.POST.get('token') 

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        if is_portion == "yes":
            fav_panel, created = FavoriteSessionPart.objects.get_or_create(user=user_obj)
            part = SessionPart.objects.filter(id=session_id).first()

            if created:
                fav_panel.session_segments.add(part)
            else:
                for obj in fav_panel.session_segments.all():
                    if obj.id == part.id:
                        fav_panel.session_segments.remove(part)
                    else:
                        fav_panel.session_segments.add(part)
        else:
            fav_panel, created = FavoriteSession.objects.get_or_create(user=user_obj)
            session = Session.objects.filter(id=session_id).first()
            
            p_list = []
            for z in fav_panel.sessions.all():
                p_list.append(z.id)
            
            if created:
                fav_panel.sessions.add(session)
            else:
                if session_id in p_list:
                    fav_panel.sessions.remove(session)
                else:
                    fav_panel.sessions.add(session)
                
        return Response({"status": "Ok"})


class ListPsychiatristView(APIView):    
    def post(self, request):
        token = request.POST.get('token') 
        
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_psych_palette, created = FavoritePsychiatrist.objects.get_or_create(user=user_obj)
        
        favs = fav_psych_palette.psychiatrists.all()
        a_list = []
        for a in favs:
            a_list.append(a.id)

        psychs = Psychiatrist.objects.all()
        b_list = []
        for b in psychs:
            b_list.append(b.id)

        loved_psych_pks = []
        neutral_psych_pks = []
        for c in b_list:
            if c in a_list:
                loved_psych_pks.append(c)
            else:
                neutral_psych_pks.append(c)

        psychList = []

        if len(loved_psych_pks) > 0:
            for loved_psych_pk in loved_psych_pks:
                x = Psychiatrist.objects.filter(id=loved_psych_pk).first()
                psychList.append({
                    "id": x.id,
                    "full_name": x.full_name,
                    "short_address": x.short_address,
                    "phone": x.phone,
                    "rating": x.rating,
                    "number_of_ratings": x.number_of_ratings,
                    "image": x.image.url,
                    "liked": True
                })

        if len(neutral_psych_pks) > 0:
            for neutral_session_pk in neutral_psych_pks:
                y = Psychiatrist.objects.filter(id=neutral_session_pk).first()
                psychList.append({
                    "id": y.id,
                    "full_name": y.full_name,
                    "short_address": y.short_address,
                    "phone": y.phone,
                    "rating": y.rating,
                    "number_of_ratings": y.number_of_ratings,
                    "image": y.image.url,
                    "liked": False
                })

        return Response(psychList)


class FavoritePsychiatristsView(APIView):    
    def post(self, request):
        token = request.POST.get('token')  

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_psych_palette, created = FavoritePsychiatrist.objects.get_or_create(user=user_obj)
        favs = fav_psych_palette.psychiatrists.all()

        psychList = []
        if len(favs) > 0:
            for fav in favs:
                psychList.append({
                    "id": fav.id,
                    "full_name": fav.full_name,
                    "short_address": fav.short_address,
                    "phone": fav.phone,
                    "rating": fav.rating,
                    "number_of_ratings": fav.number_of_ratings,
                    "image": fav.image.url,
                    "liked": True
                })
        
        return Response(psychList)
    

class SearchedPsychiatistsView(APIView): 
    def post(self, request):
        q = request.POST.get('q')   
        token = request.POST.get('token') 
        
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_psych_palette, created = FavoritePsychiatrist.objects.get_or_create(user=user_obj)

        favs = fav_psych_palette.psychiatrists.all()
        a_list = []
        for a in favs:
            a_list.append(a.id)

        psychs = Psychiatrist.objects.filter(full_name__icontains=q)
        b_list = []
        for b in psychs:
            b_list.append(b.id)

        loved_psych_pks = []
        neutral_psych_pks = []
        for c in b_list:
            if c in a_list:
                loved_psych_pks.append(c)
            else:
                neutral_psych_pks.append(c)

        psychList = []

        if len(loved_psych_pks) > 0:
            for loved_psych_pk in loved_psych_pks:
                x = Psychiatrist.objects.filter(id=loved_psych_pk).first()
                psychList.append({
                    "id": x.id,
                    "full_name": x.full_name,
                    "short_address": x.short_address,
                    "phone": x.phone,
                    "rating": x.rating,
                    "number_of_ratings": x.number_of_ratings,
                    "image": x.image.url,
                    "liked": True
                })

        if len(neutral_psych_pks) > 0:
            for neutral_session_pk in neutral_psych_pks:
                y = Psychiatrist.objects.filter(id=neutral_session_pk).first()
                psychList.append({
                    "id": y.id,
                    "full_name": y.full_name,
                    "short_address": y.short_address,
                    "phone": y.phone,
                    "rating": y.rating,
                    "number_of_ratings": y.number_of_ratings,
                    "image": y.image.url,
                    "liked": False
                })

        return Response(psychList)


class SinglePsychiatistView(APIView): 
    def post(self, request):
        psych_id = request.POST.get('psych_id')   
                
        psych_obj = Psychiatrist.objects.filter(id=psych_id).first()

        return Response({
            "full_name": psych_obj.full_name,
            "profession": psych_obj.profession,
            "full_address": psych_obj.full_address,
            "website_url": psych_obj.website_url,
            "phone": psych_obj.phone,
            "rating": psych_obj.rating,
            "image": psych_obj.image.url
        })


class LikePsychiatristView(APIView):    
    def post(self, request):
        psych_id = int(request.POST.get('id'))
        token = request.POST.get('token') 

        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        fav_psych_palette, created = FavoritePsychiatrist.objects.get_or_create(user=user_obj)
        psych_obj = Psychiatrist.objects.filter(id=psych_id).first()

        p_list = []
        for z in fav_psych_palette.psychiatrists.all():
            p_list.append(z.id)
        
        if created:
            fav_psych_palette.psychiatrists.add(psych_obj)
        else:
            if psych_id in p_list:
                fav_psych_palette.psychiatrists.remove(psych_obj)
            else:
                fav_psych_palette.psychiatrists.add(psych_obj)

        return Response({"status": "Ok"})


class FaqView(APIView):    
    def get(self, request):
        faqs = Faq.objects.all()
        faq_serializer = FaqSerializer(faqs, many=True)

        return Response(faq_serializer.data)
    

class TermView(APIView):    
    def get(self, request):
        term_page = TermsAndConditons.objects.all().order_by('-id').first()

        if term_page == None:
            desc = "Terms and conditions not added yet."
        else:
            desc = term_page.description

        return Response({"desc": desc})
    

class PrivacyView(APIView):    
    def get(self, request):
        privacy_page = PrivacyPolicy.objects.all().order_by('-id').first()
        
        if privacy_page == None:
            desc = "Privacy policy not added yet."
        else:
            desc = privacy_page.description

        return Response({"desc": desc})
    

class AddMoodView(APIView):    
    def post(self, request):
        token = request.POST.get('token') 
        feeling = request.POST.get('feeling')
        
        auth_token = AuthToken.objects.filter(token=token).first()
        user_obj = UserAccount.objects.get(email=auth_token.user.email)

        mood_obj, created = UserMood.objects.get_or_create(user=user_obj)
        mood_obj.mood = feeling
        mood_obj.save()
        
        return Response({"status": "Ok"})
    