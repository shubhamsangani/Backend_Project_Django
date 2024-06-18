from rest_framework import serializers

from .models import (Psychiatrist, FavoritePsychiatrist, Category, 
                     SessionPart, Session, FavoriteSession, Faq)


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = "__all__"
        depth = 1


class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = "__all__"