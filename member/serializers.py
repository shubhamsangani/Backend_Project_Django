from rest_framework import serializers

from .models import Profile, Event, Notification


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class UploadPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"