from django.db import models

# Create your models here.
class Prueba(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, null=False, verbose_name="Nombre del Artista")
    region = models.CharField(max_length=255, null=False, verbose_name="Región del Artista")

