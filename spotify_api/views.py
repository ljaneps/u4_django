from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from urllib.parse import quote_plus
from dotenv import load_dotenv
from .models import *
from .serializer import *
import os
import json
import base64
import requests

load_dotenv()

JSON_CREDENTIALS = 'access.json'

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

credentials = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'
encoded_credentials = base64.b64encode(
    credentials.encode('utf-8')).decode('utf-8')

headers = {
    'Authorization': f'Basic {encoded_credentials}'
}

data = {
    'grant_type': 'client_credentials'
}


class GetTokenView(APIView):

    def get(self, request):
        if os.path.exists(JSON_CREDENTIALS):
            with open(JSON_CREDENTIALS, 'r') as file:
                token_data = json.load(file)

                # Si el Token existe, se reemplaza por uno nuevo
                if 'access_token' in token_data:
                    response = requests.post(
                        'https://accounts.spotify.com/api/token', headers=headers, data=data)

                    if response.status_code == 200:
                        token_data = response.json()
                        with open(JSON_CREDENTIALS, "w") as file:
                            json.dump(token_data, file, indent=4)
                            return JsonResponse({"message": "Token reemplazado!"}, status=status.HTTP_200_OK)
                    else:
                        return JsonResponse({"detail": "Error al obtener el token"}, status=response.status_code)
            # De otro modo carga uno nuevo
            response = requests.post(
                'https://accounts.spotify.com/api/token', headers=headers, data=data)

            if response.status_code == 200:
                token_data = response.json()
                with open(JSON_CREDENTIALS, "w") as file:
                    json.dump(token_data, file, indent=4)
                    return JsonResponse({"message": "Token salvado!"}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"detail": "Error al obtener el token"}, status=response.status_code)


# ACCESO A SPOTIFY (Para no repetir código cada vez que se necesite hacer una consulta)
def access_spotify():
    if os.path.exists(JSON_CREDENTIALS):
        with open(JSON_CREDENTIALS, 'r') as file:
            token_data = json.load(file)

        if 'access_token' in token_data:
            access_token = token_data['access_token']
        else:
            return JsonResponse({"detail": "Error al recuperar el Token de accesso."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({"detail": "Error al acceder al archivo access.json."}, status=status.HTTP_404_NOT_FOUND)

    return access_token


##################################################################################
#                             GESTIÓN DE USUARIOS                                #
##################################################################################

# GET y POST
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# GET, PUT y DELETE


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "id"

##################################################################################
#                            GESTIÓN DE MÚSICA                                   #
##################################################################################


class TrackManagement(APIView):
    def get(self, request, songTitle):
        access_token = access_spotify()

        encoded_song = quote_plus(songTitle)

        url = f'https://api.spotify.com/v1/search?q={
            encoded_song}&type=track&limit=1'

        headers_sp = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(url, headers=headers_sp)

        if response.status_code == 200:
            song_data = response.json()
            if song_data['tracks']['items']:
                song_info = song_data['tracks']['items'][0]
                song_info_response = {
                    'title': song_info['name'],
                    'duration_ms': song_info['duration_ms'],
                    'artists': [artist['name'] for artist in song_info['artists']],
                    'album': song_info['album']['name'],
                    'popularity': song_info['popularity']
                }
                # Devolver los datos como respuesta JSON
                return Response(song_info_response, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Canción no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Error al recuperar información de Spotify"}, status=response.status_code)


##################################################################################
#                            GESTIÓN DE ARTISTA                                  #
##################################################################################

class ArtistManagement(APIView):

    def get(self, request, artist):
        access_token = access_spotify()

        encoded_artist = quote_plus(artist)

        url = f'https://api.spotify.com/v1/search?q={
            encoded_artist}&type=artist&limit=1'

        headers_sp = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(url, headers=headers_sp)

        if response.status_code == 200:
            artist_data = response.json()
            if artist_data['artists']['items']:
                artist_info = artist_data['artists']['items'][0]
                artist_info_response = {
                    'name': artist_info['name'],
                    'genres': artist_info['genres'],
                    'followers': artist_info['followers']['total'],
                    'popularity': artist_info['popularity']
                }
                return Response(artist_info_response, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Artista no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Error al recuperar información de Spotify"}, status=response.status_code)


##################################################################################
#                            GESTIÓN DE PLAYLIST                                   #
##################################################################################

class PlaylistManagement(APIView):

    def post(self, request, userId, song):
        print(f"userId recibido: {userId} (Tipo: {type(userId)})")

        try:
            current_user = User.objects.get(id=userId)
            print(f"Current user: {current_user.email} ")
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        track_management_view = TrackManagement()
        response = track_management_view.get(request, song)
        song_data = response.data
        print(f"song_data: {song_data}")
        # Revisa si estos datos ya existen, si no existe, lo crea
        track, created = Track.objects.get_or_create(
            title=song_data['title'],
            album=song_data['album'],
            duration_ms=song_data['duration_ms'],
            popularity=song_data['popularity']
        )

        artists = []
        for artist_name in song_data['artists']:
            artist, created = Artist.objects.get_or_create(name=artist_name)
            artists.append(artist)

        track.artists.set(artists)
        track.save()

        playlist, created = Playlist.objects.get_or_create(user=current_user)
        playlist.songs.add(track)

        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, userId):
        try:
            current_user = User.objects.get(id=userId)
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        playlist = Playlist.objects.filter(user=current_user).first()

        if not playlist:
            return Response({"detail": "Playlist no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlaylistSerializer(playlist)
        return Response(serializer.data, status=status.HTTP_200_OK)
