from django.db import models

# Modelo de datos para los usuarios
class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.name
    
# Modelo de datos para los artistas
class Artist(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
# Modelo de datos para las canciones obetnidas de Spotify
class Track(models.Model):
    title = models.CharField(max_length=50)
    duration_ms = models.IntegerField()
    album = models.CharField(max_length=50)
    artists = models.ManyToManyField('Artist') 
    popularity = models.IntegerField()
    
    def __str__(self):
        return self.title

# Modelo para la asociación de usuario y gustos musicales
class Playlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    songs = models.ManyToManyField(Track, blank=True)
    

