# GestionClient/gestion/views/rendezvous.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from gestion.models import RendezVous, Salon, Soin, Utilisateur, SoinSalonDetail
from gestion.forms.rendezvous_forms import RendezVousForm
from gestion.decorateurs import professionnel_required, eleve_or_professionnel_required


@login_required
def rendezvous_view(request):
    rendezvous = RendezVous.objects.all().order_by('date', 'heure_debut')
    context = {
        'nom_entreprise': 'Saint Jolie',
        'rendezvous': rendezvous,
        'form': RendezVousForm()
    }
    return render(request, 'gestion/rendezvous/rendezvous.html', context)


@eleve_or_professionnel_required
def ajouter_rendezvous(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    if request.method == 'POST':
        form = RendezVousForm(request.POST, salon=salon, user=request.user)
        if form.is_valid():
            rendezvous = form.save(commit=False)
            # --- LA LIGNE MANQUANTE ICI POUR ajouter_rendezvous ---
            rendezvous.heure_fin = form.cleaned_data['heure_fin']  # Récupérer heure_fin calculée
            # --- FIN DE LA LIGNE MANQUANTE ---
            rendezvous.salon = salon
            rendezvous.save()
            messages.success(request, "✅ Rendez-vous ajouté avec succès.")
            return redirect('detail_salon', pk=salon.id)
        else:
            messages.error(request, "Erreur lors de l'ajout du rendez-vous. Veuillez corriger les erreurs.")
    else:
        form = RendezVousForm(salon=salon, user=request.user)
    context = {
        'form': form,
        'salon': salon,
        'nom_entreprise': 'Saint Jolie',
    }
    return render(request, 'gestion/rendezvous/ajouter_rendezvous.html', context)


# GestionClient/gestion/views/rendezvous.py

# gestion/views/rendezvous.py

@login_required
def modifier_rendezvous(request, rendezvous_id):
    rendezvous = get_object_or_404(RendezVous, id=rendezvous_id)
    salon = rendezvous.salon

    is_personal_appointment = (not request.user.is_professional and rendezvous.utilisateur == request.user)

    if not request.user.is_professional and not is_personal_appointment:
        messages.error(request, "🚫 Vous n'avez pas l'autorisation de modifier ce rendez-vous.")
        return redirect('mes_rendezvous')

    if request.method == 'POST':
        # Lors d'une soumission, le formulaire est créé avec les données du POST
        form = RendezVousForm(
            request.POST,
            instance=rendezvous,
            salon=salon,
            user=request.user,
            for_self_appointment=is_personal_appointment
        )
        if form.is_valid():
            rendezvous = form.save(commit=False)
            rendezvous.heure_fin = form.cleaned_data['heure_fin']
            rendezvous.save()
            messages.success(request, "✅ Rendez-vous modifié avec succès.")
            if request.user.is_professional:
                return redirect('rendezvous_tous')
            else:
                return redirect('mes_rendezvous')
    else:
        # C'est ici que l'on va passer les données initiales au formulaire
        # en les formatant correctement pour les widgets HTML5.
        initial_data = {
            'date': rendezvous.date.strftime('%Y-%m-%d'),
            'heure_debut': rendezvous.heure_debut.strftime('%H:%M'),
        }
        form = RendezVousForm(
            instance=rendezvous,
            salon=salon,
            user=request.user,
            for_self_appointment=is_personal_appointment,
            initial=initial_data  # <-- On passe les données initiales ici
        )

    context = {
        'form': form,
        'rendezvous': rendezvous,
        'salon': salon,
        'nom_entreprise': 'Saint Jolie',
    }
    return render(request, 'gestion/rendezvous/modifier_rendezvous.html', context)


@login_required
def supprimer_rendezvous(request, rendezvous_id):
    rendezvous = get_object_or_404(RendezVous, id=rendezvous_id)
    if not request.user.is_professional and rendezvous.utilisateur != request.user:
        messages.error(request, "🚫 Vous n'avez pas l'autorisation de supprimer ce rendez-vous.")
        return redirect('mes_rendezvous')

    if request.method == 'POST':
        rendezvous.delete()
        messages.success(request, "🗑️ Rendez-vous supprimé avec succès.")
        if request.user.is_professional:
            return redirect('rendezvous_tous')
        else:
            return redirect('mes_rendezvous')
    return render(request, 'gestion/rendezvous/confirmer_suppression.html', {
        'rendezvous': rendezvous,  # <-- Modifiez cette ligne !
        'nom_entreprise': 'Saint Jolie',
    })


@login_required
def mes_rendezvous_view(request):
    rendezvous_list = RendezVous.objects.filter(utilisateur=request.user).order_by('date', 'heure_debut')
    context = {
        'nom_entreprise': 'Saint Jolie',
        'rendezvous_list': rendezvous_list,
        'is_my_appointments_view': True,
        'title': 'Mes rendez-vous',
    }
    return render(request, 'gestion/rendezvous/rendezvous.html', context)


@eleve_or_professionnel_required
def rendezvous_tous_view(request):
    rendezvous_list = RendezVous.objects.all().order_by('date', 'heure_debut')
    context = {
        'nom_entreprise': 'Saint Jolie',
        'rendezvous_list': rendezvous_list,
        'is_my_appointments_view': False,
        'title': 'Tous les rendez-vous',
    }
    return render(request, 'gestion/rendezvous/rendezvous.html', context)


# --- NOUVELLES VUES POUR LA PRISE DE RENDEZ-VOUS PERSONNEL ---

@login_required
def choisir_salon_pour_rendezvous(request):
    """
    Vue pour lister les salons et permettre à l'utilisateur de choisir celui pour lequel il veut prendre un rendez-vous.
    """
    # Optionnel: Préfetchez les SoinSalonDetail pour éviter N+1 requêtes si vous affichez des détails de soins ici.
    salons = Salon.objects.prefetch_related(
        Prefetch('soinsalondetail_set',
                 queryset=SoinSalonDetail.objects.select_related('soin').order_by('soin__type_de_soin'))
    ).all()

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salons': salons,
        'title': 'Choisir un Salon pour votre Rendez-vous',
    }
    return render(request, 'gestion/rendezvous/choisir_salon_pour_rendezvous.html', context)


@login_required
def prendre_rendezvous_personnel(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)

    if request.method == 'POST':
        form = RendezVousForm(request.POST, salon=salon, user=request.user, for_self_appointment=True)
        if form.is_valid():
            # ... (code pour sauvegarder)
            messages.success(request, "✅ Votre rendez-vous a été pris avec succès.")
            return redirect('mes_rendezvous')
        else:
            # Votre code passe déjà le 'form' au template ici,
            # donc la logique de la vue est correcte.
            messages.error(request, "Erreur lors de la prise de rendez-vous. Veuillez corriger les erreurs.")
    else:
        form = RendezVousForm(salon=salon, user=request.user, for_self_appointment=True)

    context = {
        'form': form,  # <-- C'est cette ligne qui permet d'afficher les erreurs
        'salon': salon,
        'nom_entreprise': 'Saint Jolie',
        'title': f"Prendre Rendez-vous chez {salon.nom}",
    }
    return render(request, 'gestion/rendezvous/prendre_rendezvous_personnel.html', context)
