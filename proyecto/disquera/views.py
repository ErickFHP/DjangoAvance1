from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
import requests # type: ignore
from django.contrib import messages

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
                    print(url)
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