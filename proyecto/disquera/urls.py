from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('artistas', views.artistas, name='artistas'),
    path('artistas/agregar', views.agregarArtista, name='agregarArtista'),
    path('artistas/buscar', views.buscarIDArtista, name='buscarIDArtista')
]