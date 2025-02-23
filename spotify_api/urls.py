from django.urls import path
from .views import *

urlpatterns = [
    path('get_token/', GetTokenView.as_view(), name='get_token'),
    path('user/', UserListCreateView.as_view(), name='user_list'),
    path('user/<int:id>/',UserDetailView.as_view(), name='user_detail'),
    path('spotify/song/<str:songTitle>', TrackManagement.as_view(), name='track_management'),
    path('spotify/artist/<str:artist>', ArtistManagement.as_view(), name='artist_management'),
    path('spotify/playlist/<int:userId>/<str:song>', PlaylistManagement.as_view(), name='playlist_management'),
    path('spotify/playlist/<int:userId>/', PlaylistManagement.as_view(), name='playlist_management_get'),

    
]