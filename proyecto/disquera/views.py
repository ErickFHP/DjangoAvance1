from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
import requests # type: ignore
from django.contrib import messages
import re #Comprobacion correo

import json

# Base URL for the API
base_url = "http://localhost:8080"

# Create your views here.

def inicio(request):
    return render(request, 'paginas/index.html')

# Views related with artists

def artistas(request):
    url = f"{base_url}/Artists"
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON response
        artists = response.json()

        # Filtra los artistas por un status mandado en URL
        status = request.GET.get('status')
        if status:
            artists = [artist for artist in artists if artist['statusArtist'] == status]

        for art in artists:
            if art['statusArtist'] == "1":
                art['statusArtist'] = 'Activo'
            else:
                art['statusArtist'] = 'Inactivo'

        return render(request, 'paginas/artistas/artistas.html', {'artistas': artists})
    else:
        error_message = f"Error fetching artists: {response.status_code}"
        return render(request, 'paginas/artistas/artistas.html', {'error': error_message})
    
def agregarArtista(request):
    if request.method == 'POST':
        if len(request.POST.get('nameArtist')) != 0 and len(request.POST.get('country')) != 0:
            url = f"{base_url}/Artists/add"
            artist_data = {
                "nameArtist": request.POST.get('nameArtist'),
                "country": request.POST.get('country'),
                "statusArtist": "0",
            }
            json_data = json.dumps(artist_data)
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, data=json_data, headers=headers)

            if response.status_code == 201:
                new_artist = response.json()
                messages.success(request, f"Artist created successfully. ID: {new_artist['idArtist']}")
            else:
                messages.error(request, f"Error creating artist: {response.status_code}")

            return render(request, 'paginas/artistas/agregarArtista.html')
        else:
            messages.error(request, "Valores inválidos")
    return render(request, 'paginas/artistas/agregarArtista.html')

def buscarIDArtista(request):
    if request.method == 'POST':
        if 'idArtist' in request.POST:
            try:
                idArtist = int(request.POST['idArtist'])
                
                url = f"{base_url}/Artists/{idArtist}"
                response = requests.get(url)
                if response.status_code == 200:
                    # Parse the JSON response
                    artist = response.json()
                    context = {
                        'idArtistContext': idArtist,
                        'nameArtist': artist['nameArtist'],
                        'country': artist['country'],
                        'statusArtist': artist['statusArtist']
                    }
                    return render(request, 'paginas/artistas/buscarIDArtista.html', context)
                else:
                    messages.error(request, f"ID no encontrado: {response.status_code}")
            except ValueError:
                messages.error(request, "El valor ingresado para idArtist no es un número entero.")
        elif 'idArtistContext' in request.POST:
            if len(request.POST['idArtistContext']) != 0:
                idArtist = int(request.POST['idArtistContext'])
                nameArtist = request.POST['nameArtist']
                country = request.POST['country']
                statusArtist = request.POST['statusArtist']
                if statusArtist not in ['0', '1']:
                    messages.error(request, "El valor de statusArtist debe ser '0' o '1'.")
                else:
                    url = f"{base_url}/Artists/update/{idArtist}"
                    actualizado = {
                        "nameArtist": nameArtist,
                        "country": country,
                        "statusArtist": statusArtist
                    }
                    json_data = json.dumps(actualizado)
                    headers = {"Content-Type": "application/json"}
                    response = requests.put(url, data=json_data, headers=headers)

                    if response.status_code == 200:
                        messages.success(request, f"Detalles del Artista: {idArtist}, {nameArtist}, {country}, {statusArtist}")
                    else:
                        messages.error(request, f"Error updating artist: {response.status_code}")

                return render(request, 'paginas/artistas/buscarIDArtista.html') 
            else:
                messages.error(request, "Tiene que hacer una búsqueda primero")
                return render(request, 'paginas/artistas/buscarIDArtista.html') 

    return render(request, 'paginas/artistas/buscarIDArtista.html')

def mandarCorreoArtistas(request):
    if request.method == 'POST':
        email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        email = request.POST['email']
        if re.search(email_regex, email):
            # El correo electrónico es válido
            url = f"{base_url}/Artists"
            response = requests.get(url)
            if response.status_code == 200:
                # Parse the JSON response
                artists = response.json()
                artist_strings = [f"  -ID {artist['idArtist']}: {artist['nameArtist']} ({artist['country']}) Estado: {'Activo' if artist['statusArtist'] == '1' else 'Inactivo'}" for artist in artists]
                # Join the artist strings with newlines for readability
                formatted_string = "\n".join(artist_strings)

                data = {
                    "email": email,
                    "message": formatted_string
                }

                json_data = json.dumps(data)
                headers = {"Content-Type": "application/json"}
                url = f"{base_url}/email/send"
                response = requests.post(url, data=json_data, headers=headers)

                if response.status_code == 200:
                    messages.success(request, f"Información enviada correctamente a {email}")
                else:
                    messages.error(request, f"Error enviando la información: {response.status_code}")
            else:
                messages.error(request, f"Error buscando los artistas: {response.status_code}")
        else:
            # El correo electrónico no es válido
            messages.error(request, f"Correo electrónico no válido: {email}")
    return render(request, 'paginas/artistas/mandarCorreoArtistas.html')

# Catalogo
def albums(request):
    url = f"{base_url}/Albums"
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON response
        albums = response.json()

        status = request.GET.get('status')

        if status != None:
            if status == "True":
                albums = [album for album in albums if album['edicion_especial']]
            else:
                albums = [album for album in albums if not album['edicion_especial']]

        for alb in albums:
            url = f"{base_url}/Artists/{alb['id_artista']}"
            response = requests.get(url)
            if response.status_code == 200:
                artista = response.json()
                alb['artista'] = artista['nameArtist']
                if alb['edicion_especial'] == True:
                    alb['edicion_especial'] = 'Especial'
                else:
                    alb['edicion_especial'] = 'Normal'

        return render(request, 'paginas/catalogo/albums.html', {'albums': albums})
    else:
        error_message = f"Error: {response.status_code}"
        return render(request, 'paginas/catalogo/albums.html', {'error': error_message})
    
def agregarAlbum(request):
    if request.method == 'POST':
        data = {
            "id_artista": int(request.POST['id_artista']),
            "fecha_lanzamiento": request.POST['fecha_lanzamiento'],
            "edicion_especial": request.POST['edicion_especial'],
            "titulo": request.POST['titulo'],
            "precio": float(request.POST['precio'])
        }

        json_data = json.dumps(data)
        headers = {"Content-Type": "application/json"}
        url = f"{base_url}/Albums/add"
        response = requests.post(url, data=json_data, headers=headers)
        if response.status_code == 201:
            messages.success(request, f"Registro creado correctamente")
        elif response.status_code == 404:
            messages.error(request, f"Error enviando la información: Id no encontrado")
        else:
            messages.error(request, f"Error enviando la información")

    return render(request, 'paginas/catalogo/agregarAlbum.html')

def buscarIDAlbum(request):
    if request.method == 'POST':
        if 'id_album' in request.POST:
            try:
                id_album = int(request.POST['id_album'])
                
                url = f"{base_url}/Albums/{id_album}"
                response = requests.get(url)
                if response.status_code == 200:
                    # Parse the JSON response
                    album = response.json()
                    context = {
                        'id_album_context': id_album,
                        'titulo': album['titulo'],
                        'precio': album['precio'],
                        'edicion_especial': "true" if album['edicion_especial'] == True else "false",
                        'fecha_lanzamiento': album['fecha_lanzamiento'],
                    }
                    return render(request, 'paginas/catalogo/buscarIDAlbum.html', context)
                else:
                    messages.error(request, f"ID no encontrado: {response.status_code}")
            except ValueError:
                messages.error(request, "El valor ingresado para id_album no es un número entero.")
        elif 'id_album_context' in request.POST:
            if len(request.POST['id_album_context']) != 0:
                id_album = int(request.POST['id_album_context'])
                url = f"{base_url}/Albums/update/{id_album}"
                actualizado = {
                    'titulo': request.POST['titulo'],
                    'precio': float(request.POST['precio']),
                    'edicion_especial': request.POST['edicion_especial'],
                    'fecha_lanzamiento': request.POST['fecha_lanzamiento'],
                }
                json_data = json.dumps(actualizado)
                headers = {"Content-Type": "application/json"}
                response = requests.put(url, data=json_data, headers=headers)

                if response.status_code == 200:
                    messages.success(request, f"Registro actualizado correctamente")
                else:
                    messages.error(request, f"Error actualizando el registro: {response.status_code}")

                return render(request, 'paginas/catalogo/buscarIDAlbum.html')
            else:
                messages.error(request, "Tiene que hacer una búsqueda primero")
                return render(request, 'paginas/catalogo/buscarIDAlbum.html')
    return render(request, 'paginas/catalogo/buscarIDAlbum.html')