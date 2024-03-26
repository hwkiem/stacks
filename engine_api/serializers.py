# todo/todo_api/serializers.py
from rest_framework import serializers
from .models import BookAuthors, Books, BuildWorks, Playlists

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = '__all__'

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookAuthors
        fields = '__all__'

class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildWorks
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlists
        fields = '__all__'

# TODO: Playlist
