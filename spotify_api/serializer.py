from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email'] 

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id','name'] 

class TrackSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(many=True)
    class Meta:
        model = Track
        fields = ['id', 'title', 'album', 'duration_ms', 'popularity', 'artists'] 
        
class PlaylistSerializer(serializers.ModelSerializer):
        user = UserSerializer() 
        songs = TrackSerializer(many=True)

        class Meta:
            model = Playlist
            fields = ['id', 'user', 'songs']