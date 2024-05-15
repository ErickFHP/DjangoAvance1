from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('index', views.index, name='index'),
    path('artistas', views.artistas, name='artistas'),
    path('artistas/agregar', views.agregarArtista, name='agregarArtista'),
    path('artistas/buscar', views.buscarIDArtista, name='buscarIDArtista'),
    path('artistas/correo', views.mandarCorreoArtistas, name='mandarCorreoArtistas'),
    path('catalogo/albums', views.albums, name='albums'),
    path('catalogo/albums/agregar', views.agregarAlbum, name='agregarAlbum'),
    path('catalogo/albums/buscar', views.buscarIDAlbum, name='buscarIDAlbum'),
]