# gestion/views/soin_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from gestion.forms.soin_forms import SoinForm, SoinSalonDetailForm
from gestion.models import Soin, Salon, SoinSalonDetail, \
    RendezVous  # Assure-toi d'importer RendezVous si utilisé ailleurs
from gestion.decorateurs import professionnel_required  # Assure-toi que le chemin est correct


# Les imports suivants ne sont plus strictement nécessaires ici si la gestion de durée/prix est dans les forms
# ou si ces vues ne manipulent plus directement ces champs via request.POST
# from datetime import timedelta # Plus nécessaire car géré par le formulaire
# from decimal import Decimal, InvalidOperation # Plus nécessaire ici
# from django.db import IntegrityError  # Utile pour gérer les unique_together sur SoinSalonDetail


# --- VUES POUR LES SOINS ET LEURS DÉTAILS (VERSION CORRECTE ET SÉPARÉE) ---


def soin_list(request):
    """
    Affiche la liste de tous les salons, permettant de gérer les soins par salon.
    """
    salons = Salon.objects.all().order_by('nom')  # Récupère tous les salons
    context = {
        'nom_entreprise': "Saint Jolie",
        'salons': salons,
        'title': "Gestion des Soins par Salon",  # Nouveau titre pour cette vue
    }
    return render(request, 'gestion/soin/soins.html', context)


@professionnel_required
def soin_create_general(request):
    """
    Vue pour créer un nouveau Soin (un type de soin général, sans prix ni salon spécifique).
    Utilise SoinForm qui ne contient que 'type_de_soin' et 'duree'.
    """
    if request.method == 'POST':
        form = SoinForm(request.POST)  # Instancie SoinForm avec les données postées
        if form.is_valid():
            soin = form.save()  # Sauvegarde le nouveau Soin général
            messages.success(request,
                             f"Le type de soin '{soin.type_de_soin}' a été créé avec succès ! ✅ Vous pouvez "
                             f"maintenant y ajouter des détails par salon.")
            return redirect('soins')  # Redirige vers la liste des SoinSalonDetail
        else:
            messages.error(request, "❌ Veuillez corriger les erreurs dans le formulaire du type de soin général.")
            # Afficher les erreurs du formulaire dans la console pour le débogage
            print("Erreurs du formulaire SoinForm:", form.errors)  # Aide au débogage
    else:
        form = SoinForm()  # Pour une requête GET, affiche un formulaire vide

    return render(request, 'gestion/soin/soin_form.html', {
        'form': form,
        'title': 'Ajouter un nouveau type de soin général',  # Titre du formulaire
        'nom_entreprise': 'Saint Jolie',
    })


@professionnel_required
def soin_update_general(request, pk):
    """
    Vue pour modifier un Soin (type de soin général) existant.
    """
    soin = get_object_or_404(Soin, pk=pk)  # Récupère le Soin général à modifier
    if request.method == 'POST':
        form = SoinForm(request.POST, instance=soin)  # Rempli le formulaire avec les données et l'instance existante
        if form.is_valid():
            form.save()
            messages.success(request, f"Le type de soin '{soin.type_de_soin}' a été mis à jour avec succès ! ✏️")
            return redirect('soins')
        else:
            messages.error(request, "❌ Erreur lors de la mise à jour du type de soin général.")
            print("Erreurs du formulaire SoinForm (update):", form.errors)  # Aide au débogage
    else:
        form = SoinForm(instance=soin)  # Pour un GET, pré-rempli le formulaire avec les données du soin existant

    return render(request, 'gestion/soin/soin_form.html', {
        'form': form,
        'title': f'Modifier le type de soin : {soin.type_de_soin}',
        'nom_entreprise': 'Saint Jolie',
    })


@professionnel_required
def soin_delete_general(request, pk):
    """
    Vue pour supprimer un Soin (type de soin général).
    ATTENTION : La suppression d'un Soin entraînera la suppression CASCADING
    de tous les SoinSalonDetail qui y sont liés.
    """
    soin = get_object_or_404(Soin, pk=pk)
    if request.method == 'POST':
        soin.delete()
        messages.success(request,
                         f"Le type de soin '{soin.type_de_soin}' et tous ses détails associés ont été supprimés avec "
                         f"succès. 🗑️")
        return redirect('soins')

    # Pour une requête GET, afficher une page de confirmation de suppression
    return render(request, 'gestion/soin/confirm_delete.html', {
        'object': soin,
        'type': 'type de soin général',
        'return_url': 'soins',
        'nom_entreprise': 'Saint Jolie',
        'title': f'Confirmer la suppression de {soin.type_de_soin}'
    })


def soin_salon_detail_list(request, salon_pk):
    """
    Affiche la liste des SoinSalonDetail pour un salon spécifique.
    Permet de voir les soins proposés par ce salon.
    """
    salon = get_object_or_404(Salon, pk=salon_pk)
    # Récupère tous les SoinSalonDetail liés à ce salon
    soins_details = SoinSalonDetail.objects.filter(salon=salon).order_by('soin__type_de_soin')

    context = {
        'nom_entreprise': "Saint Jolie",
        'salon': salon,
        'soins_details': soins_details,
        'title': f"Soins proposés par {salon.nom}",
    }
    return render(request, 'gestion/soin/soin_salon_detail_list.html', context)


@professionnel_required
def soin_salon_detail_create(request, salon_pk):
    """
    Permet de créer un nouveau SoinSalonDetail pour un salon spécifique.
    Gère les cas où le SoinSalonDetail existe déjà pour éviter les erreurs de doublon.
    """
    salon = get_object_or_404(Salon, pk=salon_pk)

    if request.method == 'POST':
        # Passer le salon au formulaire si votre formulaire SoinSalonDetailForm en a besoin
        # pour filtrer les soins par exemple (bien que pas strictement nécessaire pour la sauvegarde)
        form = SoinSalonDetailForm(request.POST)
        if form.is_valid():
            soin_detail = form.save(commit=False)
            soin_detail.salon = salon  # Associe le SoinSalonDetail au salon

            # --- DÉBUT DE LA NOUVELLE LOGIQUE DE VÉRIFICATION DES DOUBLONS ---
            # Vérifie si un SoinSalonDetail avec la même paire (soin, salon) existe déjà
            existing_soin_detail = SoinSalonDetail.objects.filter(
                soin=soin_detail.soin,
                salon=soin_detail.salon
            ).first()  # .first() retourne le premier objet trouvé ou None si aucun n'est trouvé

            if existing_soin_detail:
                # Si un doublon est trouvé, affiche un message d'avertissement
                messages.warning(request,
                                 f'Le soin "{soin_detail.soin.type_de_soin}'
                                 f'" est déjà associé à ce salon. Vous pouvez le modifier si nécessaire.')
                # Redirige l'utilisateur vers la liste des soins du salon
                return redirect('soin_salon_detail_list', salon_pk=salon.pk)
            # --- FIN DE LA NOUVELLE LOGIQUE DE VÉRIFICATION DES DOUBLONS ---

            soin_detail.save()  # Si pas de doublon, sauvegarde le nouvel objet
            messages.success(request, 'Le soin spécifique a été ajouté avec succès à ce salon !')
            return redirect('soin_salon_detail_list', salon_pk=salon.pk)
        else:
            # Si le formulaire n'est pas valide (par ex. champ requis manquant), affiche une erreur
            messages.error(request, 'Erreur lors de l\'ajout du soin spécifique. Veuillez vérifier les champs.')
            print("Erreurs du formulaire SoinSalonDetailForm (create):", form.errors)  # Aide au débogage
    else:
        # Pour une requête GET, initialise le formulaire
        # Si 'salon' est un HiddenInput dans le formulaire, passer le PK du salon via 'initial' est une bonne pratique.
        form = SoinSalonDetailForm(initial={
            'salon': salon.pk})  # Utilisez salon.pk si le champ salon dans le form est un ModelChoiceField caché

    context = {
        'nom_entreprise': "Saint Jolie",
        'form': form,
        'salon': salon,  # Passe l'objet salon au template pour l'affichage
        'title': f"Ajouter un soin pour {salon.nom}",
    }
    return render(request, 'gestion/soin/soin_salon_detail_form.html', context)


@professionnel_required
def soin_salon_detail_update(request, pk):
    """
    Permet de modifier un SoinSalonDetail existant.
    """
    soin_detail = get_object_or_404(SoinSalonDetail, pk=pk)
    salon = soin_detail.salon  # Récupère le salon associé au soin_detail

    if request.method == 'POST':
        # Instancie le formulaire avec les données POST et l'instance existante
        form = SoinSalonDetailForm(request.POST, instance=soin_detail)
        if form.is_valid():
            form.save()  # Le formulaire s'occupe de la conversion duree_minutes -> timedelta
            messages.success(request, 'Le détail du soin a été mis à jour avec succès !')
            # Redirige vers la liste des soins spécifiques de CE salon
            return redirect('soin_salon_detail_list', salon_pk=salon.pk)
        else:
            messages.error(request, 'Erreur lors de la mise à jour du détail du soin. Veuillez vérifier les champs.')
            print("Erreurs du formulaire SoinSalonDetailForm (update):", form.errors)  # Aide au débogage
    else:
        # Pour une requête GET, instancie le formulaire avec les données existantes
        form = SoinSalonDetailForm(instance=soin_detail)

    context = {
        'nom_entreprise': "Saint Jolie",
        'form': form,
        'salon': salon,  # Passe l'objet salon au template
        'title': f"Modifier le soin '{soin_detail.soin.type_de_soin}' pour {salon.nom}",
    }
    # Utilise le même template que pour la création (soin_salon_detail_form.html)
    return render(request, 'gestion/soin/soin_salon_detail_form.html', context)


@professionnel_required
def soin_salon_detail_delete(request, pk):
    """
    Permet de supprimer un SoinSalonDetail existant.
    """
    soin_detail = get_object_or_404(SoinSalonDetail, pk=pk)
    salon = soin_detail.salon  # Récupère le salon pour la redirection

    if request.method == 'POST':
        soin_detail.delete()
        messages.success(request, 'Le détail du soin a été supprimé avec succès !')
        return redirect('soin_salon_detail_list', salon_pk=salon.pk)
    else:
        # Pour une requête GET, afficher une page de confirmation de suppression
        context = {
            'nom_entreprise': "Saint Jolie",
            'soin_detail': soin_detail,
            'salon': salon,
            'title': f"Confirmer la suppression du soin '{soin_detail.soin.type_de_soin}' de {salon.nom}",
        }
        return render(request, 'gestion/soin/soin_salon_detail_confirm_delete.html', context)
