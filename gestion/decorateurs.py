# GestionClient/gestion/decorateurs.py

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

# Importe le modèle Utilisateur pour pouvoir accéder à son champ 'role'
# (Même si on a déjà mis des propriétés dans le modèle, c'est une bonne pratique
# d'importer le modèle si tu utilises ses champs directement ici)
from gestion.models import Utilisateur


def est_professionnel(user):
    """
    Vérifie si l'utilisateur est authentifié et est considéré comme un professionnel.
    Nous utilisons le champ 'is_staff' de Django pour cela.
    """
    return user.is_authenticated and user.is_staff


# --- DÉBUT MODIFICATION : AJOUT DE LA FONCTION POUR LE RÔLE 'ÉLÈVE' ---
def est_eleve(user):
    """
    Vérifie si l'utilisateur est authentifié et a le rôle 'eleve'.
    On s'assure que l'utilisateur a bien l'attribut 'role' (ce qui est le cas après notre migration).
    """
    return user.is_authenticated and hasattr(user, 'role') and user.role == 'eleve'


# --- FIN MODIFICATION ---


def professionnel_required(view_func):
    """
    Décorateur pour s'assurer que l'utilisateur est un professionnel connecté.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Veuillez vous connecter pour accéder à cette page. 🚫")
            return redirect('login')

        if not est_professionnel(request.user):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page. ⛔")
            return redirect('home')
        return view_func(request, *args, **kwargs)

    return wrapper


# --- DÉBUT MODIFICATION : AJOUT DU NOUVEAU DÉCORATEUR POUR ÉLÈVE OU PROFESSIONNEL ---
def eleve_or_professionnel_required(view_func):
    """
    Décorateur pour s'assurer que l'utilisateur est un élève OU un professionnel connecté.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Veuillez vous connecter pour accéder à cette page. 🚫")
            return redirect('login')

        # Vérifie si l'utilisateur est soit un professionnel, soit un élève
        if not (est_professionnel(request.user) or est_eleve(request.user)):
            messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page. ⛔")
            return redirect('home')  # Redirige vers la page d'accueil si ni pro ni élève
        return view_func(request, *args, **kwargs)

    return wrapper
