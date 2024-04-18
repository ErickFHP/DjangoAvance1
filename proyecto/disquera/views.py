from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
import requests # type: ignore

# Base URL for the API
base_url = "http://localhost:8080/Artists"

# Create your views here.

def inicio(request):
    return render(request, 'paginas/index.html')

def artistas(request):
    response = requests.get(base_url)

    if response.status_code == 200:
        # Parse the JSON response
        artists = response.json()

        # Filter artists based on status (if requested via query parameters)
        status = request.GET.get('status')  # Retrieve status value from URL query string
        if status:
            artists = [artist for artist in artists if artist['statusArtist'] == status]

        # Convert status values to human-readable labels in artists dictionary
        for art in artists:
            if art['statusArtist'] == "1":
                art['statusArtist'] = 'Activo'
            else:
                art['statusArtist'] = 'Inactivo'

        # Pass filtered and labeled data to the template
        return render(request, 'paginas/artistas.html', {'artistas': artists})
    else:
        # Handle API request errors gracefully
        error_message = f"Error fetching artists: {response.status_code}"
        return render(request, 'paginas/artistas.html', {'error': error_message})