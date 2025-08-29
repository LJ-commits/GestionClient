# gestion/views/utilisateur_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models.functions import Lower
from django.contrib.auth.forms import SetPasswordForm

from django.db.models import Q
from django.db.models.functions import Lower

# Importe vos modèles et formulaires spécifiques
from gestion.models import Utilisateur
from gestion.forms.utilisateur_forms import UtilisateurCreationForm, UtilisateurChangeForm

# --- DÉBUT MODIFICATION : IMPORTS DES DÉCORATEURS ---
# Ancienne ligne: from gestion.decorateurs import professionnel_required
# On importe maintenant les deux décorateurs nécessaires
from gestion.decorateurs import professionnel_required, eleve_or_professionnel_required

User = get_user_model()


# Assure-toi que ROLES est bien défini ou importé si tu l'utilises.
# Si c'est une constante locale que tu as définie, elle pourrait ressembler à ça :
# ROLES = [('client', 'Client'), ('professionnel', 'Professionnel')]


# --- DÉBUT MODIFICATION : DÉCORATEUR POUR utilisateur_list ---
# Remplacer @professionnel_required par @eleve_or_professionnel_required
@eleve_or_professionnel_required
def utilisateur_list(request):
    show_inactive = request.GET.get('inactive', 'false').lower() == 'true'
    query = request.GET.get('q')  # Récupère le terme de recherche

    # Commencez avec la liste de tous les utilisateurs (sauf les superutilisateurs)
    utilisateurs = Utilisateur.objects.all().exclude(is_superuser=True)

    # Appliquez le filtre de recherche si une requête est présente
    if query:
        utilisateurs = utilisateurs.filter(
            Q(last_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    # Appliquez le filtre actif/inactif
    if show_inactive:
        utilisateurs = utilisateurs.filter(is_active=False)
    else:
        utilisateurs = utilisateurs.filter(is_active=True)

    # Triez les résultats
    utilisateurs = utilisateurs.order_by(Lower('last_name'), Lower('first_name'))

    context = {
        'nom_entreprise': "Saint Jolie",
        'utilisateurs': utilisateurs,
        'show_inactive': show_inactive,
        'title': "Liste des Utilisateurs",
        'query': query,  # <-- pour que la boxe (la variable query) recherche se souvient ce que l'utilisateur à écrit
    }
    return render(request, 'gestion/utilisateur/utilisateurs.html', context)


# Les vues suivantes restent sous @professionnel_required car elles modifient des données
# et sont réservées aux professionnels.
@eleve_or_professionnel_required
def utilisateur_create(request):
    if request.method == 'POST':
        form = UtilisateurCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"✅ L'utilisateur {user.first_name} {user.last_name} a été créé avec succès.")
            return redirect('utilisateur_list')
        else:
            messages.error(request, "⚠️ Erreur lors de l'ajout de l'utilisateur. Veuillez corriger les champs.")
            print(form.errors)

    else:
        form = UtilisateurCreationForm()

    context = {
        'action': 'Ajouter',
        'form': form,
        'user': None,
        'nom_entreprise': 'Saint Jolie',
        'title': 'Créer un nouvel utilisateur',
    }
    return render(request, 'gestion/utilisateur/utilisateur_form.html', context)


@professionnel_required
def utilisateur_update(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        form = UtilisateurChangeForm(request.POST, instance=utilisateur)
        if form.is_valid():
            user = form.save()
            messages.success(request,
                             f"L'utilisateur {user.first_name} {user.last_name} a été mis à jour avec succès ! ✏️")
            return redirect('utilisateur_list')
        else:
            messages.error(request, "⚠️ Erreur lors de la mise à jour de l'utilisateur. Veuillez corriger les champs.")
            print(form.errors)

    else:
        form = UtilisateurChangeForm(instance=utilisateur)

    context = {
        'action': 'Modifier',
        'form': form,
        'user': utilisateur,
        'nom_entreprise': 'Saint Jolie',
        'title': f'Modifier l\'utilisateur : {utilisateur.first_name} {utilisateur.last_name}'
    }
    return render(request, 'gestion/utilisateur/utilisateur_form.html', context)


@professionnel_required
def utilisateur_delete(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        utilisateur.delete()
        messages.success(request,
                         f"🗑️ L'utilisateur {utilisateur.first_name} {utilisateur.last_name} a été supprimé avec "
                         f"succès.")
        return redirect('utilisateur_list')
    return render(request, 'gestion/utilisateur/confirmer_suppression.html', {
        'object': utilisateur,
        'type': 'utilisateur',
        'return_url': 'utilisateur_list',
        'title': f'Confirmer la suppression de {utilisateur.first_name} {utilisateur.last_name}',
        'nom_entreprise': 'Saint Jolie'
    })


@professionnel_required
def utilisateur_toggle_active(request, pk):
    utilisateur = get_object_or_404(User, pk=pk)

    utilisateur.is_active = not utilisateur.is_active
    utilisateur.save()

    if utilisateur.is_active:
        messages.success(request,
                         f"✅ L'utilisateur {utilisateur.first_name} {utilisateur.last_name} est maintenant actif.")
    else:
        messages.warning(request,
                         f"⛔ L'utilisateur {utilisateur.first_name} {utilisateur.last_name} est maintenant inactif.")

    return redirect('utilisateur_list')


@eleve_or_professionnel_required
def utilisateur_set_password(request, pk):
    utilisateur_cible = get_object_or_404(Utilisateur, pk=pk)

    if request.method == 'POST':
        form = SetPasswordForm(utilisateur_cible, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                             f'Le mot de passe de {utilisateur_cible.username} a été mis à jour avec succès.')
            return redirect('utilisateur_list')
    else:
        form = SetPasswordForm(utilisateur_cible)

    context = {
        'title': f'Réinitialiser le mot de passe pour {utilisateur_cible.username}',
        'utilisateur_cible': utilisateur_cible,
        'form': form,
        'nom_entreprise': 'Saint Jolie',
    }
    return render(request, 'gestion/utilisateur/set_password_form.html', context)
