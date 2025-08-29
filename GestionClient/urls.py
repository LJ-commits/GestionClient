# GestionClient/urls.py (fichier du projet principal)

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('accueil/')),  # Redirige la racine vers /accueil/
    path('', include('gestion.urls')),  # Inclut les URLs de ton application 'gestion'
]
