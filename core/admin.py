from django.contrib import admin

from core.models import (Psychiatrist, FavoritePsychiatrist, Category, SessionPart, Session, FavoriteSession, FavoriteSessionPart, CompletedSessionDuration,
                        Faq, TermsAndConditons, PrivacyPolicy, UserMood,
                        RecentSessionView)

admin.site.register([
    Psychiatrist, 
    FavoritePsychiatrist, 
    Category, 
    SessionPart, 
    Session, 
    FavoriteSession,
    FavoriteSessionPart,
    CompletedSessionDuration,
    Faq,
    TermsAndConditons,
    PrivacyPolicy,
    UserMood, 
    RecentSessionView
])
