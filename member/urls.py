from django.urls import path
from .views import *


urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('verify/', ActivationView.as_view()),
    path('recover/', RecoverView.as_view()),
    path('reset-otp/', ResetOtpView.as_view()),
    path('reset/', PasswordResetView.as_view()),
    path('get-profile/', ProfileInfo.as_view()),
    path('post-profile/', ProfileInformation.as_view()),
    path('pic/', ProfilePic.as_view()),
    path('calendar/', EventCalendarView.as_view()),
    path('event-list/', EventListView.as_view()),
    path('notification-list/', NotificationsView.as_view()),
    path('today-event-list/', TodayEventListView.as_view()),
    path('event-day/', EventDayView.as_view()),
    path('event-detail/', EventDetailView.as_view()),
    path('add-event/', AddEventView.as_view()),
    path('update-event/', EditEventView.as_view()),
    path('delete-event/', DeleleEventView.as_view()),
    path('mark-event/', MarkEventView.as_view()),
    path('task-count/', CompletedTasksCountView.as_view()),
]