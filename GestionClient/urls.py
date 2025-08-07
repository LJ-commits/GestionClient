# GestionClient/urls.py (fichier du projet principal)

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from gestion.views import main_views  # Si tu as une main_views pour tes pages principales

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('home/')),  # Redirige la racine vers /home/
    path('', include('gestion.urls')),  # Inclut les URLs de ton application 'gestion'
]
