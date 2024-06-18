from django.urls import path
from .views import *


urlpatterns = [
    path('recommended-list-sessions/', RecommendedListSessionsView.as_view()),
    path('main-home/', MainHomeView.as_view()),
    path('home-profile/', HomeProfileView.as_view()),
    path('faq/', FaqView.as_view()),
    path('term/', TermView.as_view()),
    path('privacy/', PrivacyView.as_view()),
    path('add-mood/', AddMoodView.as_view()),
    path('fav-sessions/', FavoriteSessionsView.as_view()),
    path('list-sessions/', ListSessionsView.as_view()),
    path('categorized-sessions/', CategorizedSessionsView.as_view()),
    path('searched-sessions/', SearchedSessionsView.as_view()),
    path('single-session/', SingleSessionView.as_view()),
    path('content/', ContentView.as_view()),
    path('add-duration/', AddDurationView.as_view()),
    path('add-liking/', AddLikingView.as_view()),
    path('list-psych/', ListPsychiatristView.as_view()),
    path('fav-psychs/', FavoritePsychiatristsView.as_view()),
    path('searched-psych/', SearchedPsychiatistsView.as_view()),
    path('single-psych/', SinglePsychiatistView.as_view()),
    path('like-psych/', LikePsychiatristView.as_view()),
]