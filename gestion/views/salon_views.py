# GestionClient/gestion/views/salon_views.py
from collections import defaultdict
from datetime import datetime, timedelta, date
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import formats

from gestion.decorateurs import professionnel_required, eleve_or_professionnel_required
from gestion.forms.salon_forms import SalonForm
# NOUVEAU: Importer JourSpecial et PlageHoraireSpeciale
from gestion.models import Salon, RendezVous, Jour, PlageHoraire, JourSpecial, PlageHoraireSpeciale


# --- VUES LIÉES AUX SALONS UNIQUEMENT ---

@login_required
def liste_salons(request):
    salons = Salon.objects.all()
    context = {
        'nom_entreprise': 'Saint Jolie',
        'salons': salons,
    }
    return render(request, 'gestion/salon/liste_salons.html', context)


def detail_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)

    # NOUVEAU : Récupération de l'URL de la page précédente (HTTP_REFERER)
    referer = request.META.get('HTTP_REFERER')

    # Récupération et organisation des plages horaires régulières
    jours_semaine = Jour.objects.order_by('numero')
    horaires_par_jour = {}
    for jour in jours_semaine:
        horaires_par_jour[jour.nom] = PlageHoraire.objects.filter(salon=salon, jour=jour).order_by('heure_debut')

    # --- Logique de regroupement des jours spéciaux ---
    all_jours_speciaux = JourSpecial.objects.filter(salon=salon).order_by('date')
    grouped_jours_speciaux = []
    current_period = None

    for js in all_jours_speciaux:
        if js.est_ferme:
            if (current_period and current_period['type'] == 'period_ferme' and js.date ==
                    current_period['date_fin'] + timedelta(days=1)):
                current_period['date_fin'] = js.date
                current_period['ids'].append(js.id)
            else:
                if current_period:
                    grouped_jours_speciaux.append(current_period)
                current_period = {
                    'type': 'period_ferme',
                    'date_debut': js.date,
                    'date_fin': js.date,
                    'est_ferme': True,
                    'ids': [js.id]
                }
        else:
            if current_period:
                grouped_jours_speciaux.append(current_period)
            grouped_jours_speciaux.append({
                'type': 'single_jour',
                'jour_special': js,
                'est_ferme': False,
                'plages_speciales': list(js.plages_specifiques.all())
            })
            current_period = None

    if current_period:
        grouped_jours_speciaux.append(current_period)
    # --- Fin de la logique de regroupement des jours spéciaux ---

    # --- DÉBUT MODIFICATION : Logique de regroupement des rendez-vous par mois ---
    rendezvous_par_mois = defaultdict(list)

    # NOUVELLE LOGIQUE : Si l'utilisateur est un professionnel OU un élève, il voit TOUS les rendez-vous du salon.
    if request.user.is_professional or request.user.role == 'eleve':
        rendezvous_futurs = RendezVous.objects.filter(
            salon=salon,
            date__gte=date.today()
        ).order_by('date', 'heure_debut')

        if rendezvous_futurs:
            for rd in rendezvous_futurs:
                mois_annee_key = formats.date_format(rd.date, "F Y").capitalize()
                rendezvous_par_mois[mois_annee_key].append(rd)
    # --- FIN MODIFICATION ---

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'horaires_par_jour': horaires_par_jour,
        'grouped_jours_speciaux': grouped_jours_speciaux,
        'rendezvous_par_mois': dict(rendezvous_par_mois),
        # NOUVEAU : Passer l'URL de la page précédente au template
        'referer': referer,
    }
    return render(request, 'gestion/salon/detail_salon.html', context)


@eleve_or_professionnel_required
def anciens_rendezvous(request, pk):
    salon = get_object_or_404(Salon, pk=pk)

    # Récupérer les rendez-vous passés du salon
    anciens_rendezvous_list = RendezVous.objects.filter(
        salon=salon,
        date__lt=date.today()
    ).order_by('-date', '-heure_debut')  # Trier du plus récent au plus ancien

    # Grouper les rendez-vous par mois
    rendezvous_par_mois = defaultdict(list)
    for rd in anciens_rendezvous_list:
        mois_annee_key = formats.date_format(rd.date, "F Y").capitalize()
        rendezvous_par_mois[mois_annee_key].append(rd)

    context = {
        'salon': salon,
        'rendezvous_par_mois': dict(rendezvous_par_mois),
        'title': f'Anciens Rendez-vous pour {salon.nom}',
        'nom_entreprise': 'Saint Jolie',
    }
    return render(request, 'gestion/salon/anciens_rendezvous.html', context)


@professionnel_required
def ajouter_salon(request):
    if request.method == 'POST':
        form = SalonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Salon ajouté avec succès.")
            return redirect('liste_salons')
    else:
        form = SalonForm()
    context = {
        'form': form,
        'nom_entreprise': 'Saint Jolie',
    }
    return render(request, 'gestion/salon/ajouter_salon.html', context)


@professionnel_required
def modifier_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    if request.method == 'POST':
        form = SalonForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Salon modifié avec succès.")
            return redirect('detail_salon', pk=salon.id)
    else:
        form = SalonForm(instance=salon)
    context = {
        'form': form,
        'salon': salon,
        'nom_entreprise': 'Saint Jolie',
    }
    return render(request, 'gestion/salon/modifier_salon.html', context)


@professionnel_required
def supprimer_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    if request.method == 'POST':
        salon.delete()
        messages.success(request, "🗑️ Salon supprimé avec succès.")
        return redirect('liste_salons')
    return render(request, 'gestion/salon/confirmer_suppression.html', {
        'objet': salon,
        'nom_entreprise': 'Saint Jolie',
    })
