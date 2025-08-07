# gestion/admin.py
from django.contrib import admin
from .models import RendezVous, Salon, Soin, SoinSalonDetail, Utilisateur, Jour, PlageHoraire, JourSpecial, \
    PlageHoraireSpeciale  # Assurez-vous d'importer tous vos modèles

# Enregistrez vos modèles ici
admin.site.register(RendezVous)  # Ajoutez cette ligne
admin.site.register(Salon)
admin.site.register(Soin)
admin.site.register(SoinSalonDetail)
admin.site.register(Utilisateur)  # Utilisateur est déjà là, mais c'est un bon exemple
admin.site.register(Jour)
admin.site.register(PlageHoraire)
admin.site.register(JourSpecial)
admin.site.register(PlageHoraireSpeciale)
