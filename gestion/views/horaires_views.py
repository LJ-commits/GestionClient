# gestion/views/horaires_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from gestion.models import Salon, PlageHoraire, JourSpecial, PlageHoraireSpeciale
from gestion.forms.horaire_forms import PlageHoraireForm, JourSpecialForm, PlageHoraireSpecialeForm, PeriodeVacancesForm
from django.contrib.auth.decorators import login_required
from gestion.decorateurs import professionnel_required
from datetime import date, timedelta


# --- Vues pour les Plages Horaires régulières ---

@professionnel_required
def liste_plages_horaires(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    # Récupère les plages horaires triées par jour (numéro) puis par heure de début
    plages_horaires = PlageHoraire.objects.filter(salon=salon).order_by('jour__numero', 'heure_debut')

    # Pour afficher les jours spéciaux et leurs plages (à implémenter plus tard)
    jours_speciaux = JourSpecial.objects.filter(salon=salon).order_by('date')

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'plages_horaires': plages_horaires,
        'jours_speciaux': jours_speciaux,  # Pour la future section
    }
    return render(request, 'gestion/salon/plage_horaire/liste_plages_horaires.html', context)


@professionnel_required
def ajouter_plage_horaire(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    if request.method == 'POST':
        form = PlageHoraireForm(request.POST, salon=salon)  # Passe le salon au formulaire pour la validation
        if form.is_valid():
            plage_horaire = form.save(commit=False)
            plage_horaire.salon = salon
            plage_horaire.save()
            messages.success(request, "✅ Plage horaire ajoutée avec succès.")
            return redirect('liste_plages_horaires', pk=salon.id)
    else:
        form = PlageHoraireForm(salon=salon)  # Passe le salon au formulaire
    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'form': form,
    }
    return render(request, 'gestion/salon/plage_horaire/ajouter_plage_horaire.html', context)


@professionnel_required
def modifier_plage_horaire(request, salon_pk, plage_pk):  # pk du salon et pk de la plage
    salon = get_object_or_404(Salon, pk=salon_pk)
    plage_horaire = get_object_or_404(PlageHoraire, pk=plage_pk,
                                      salon=salon)  # S'assurer que la plage appartient bien au salon

    if request.method == 'POST':
        form = PlageHoraireForm(request.POST, instance=plage_horaire, salon=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Plage horaire modifiée avec succès.")
            return redirect('liste_plages_horaires', pk=salon.id)
    else:
        form = PlageHoraireForm(instance=plage_horaire, salon=salon)
    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'form': form,
        'plage_horaire': plage_horaire,
    }
    return render(request, 'gestion/salon/plage_horaire/modifier_plage_horaire.html', context)


@professionnel_required
def supprimer_plage_horaire(request, salon_pk, plage_pk):  # pk du salon et pk de la plage
    salon = get_object_or_404(Salon, pk=salon_pk)
    plage_horaire = get_object_or_404(PlageHoraire, pk=plage_pk, salon=salon)

    if request.method == 'POST':
        plage_horaire.delete()
        messages.success(request, "🗑️ Plage horaire supprimée avec succès.")
        return redirect('liste_plages_horaires', pk=salon.id)

    return render(request, 'gestion/salon/plage_horaire/confirmer_suppression_plage_horaire.html', {
        'plage': plage_horaire,
        'salon': salon,
        'nom_entreprise': 'Saint Jolie',
    })


# --- Vues pour les Jours Spéciaux ---

@professionnel_required
def liste_jours_speciaux(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    # Récupère tous les jours spéciaux, triés par date
    all_jours_speciaux = JourSpecial.objects.filter(salon=salon).order_by('date')

    grouped_jours_speciaux = []
    current_period = None

    for js in all_jours_speciaux:
        # Si le jour spécial est une fermeture complète
        if js.est_ferme:
            if (current_period and current_period['type'] == 'period_ferme' and js.date == current_period['date_fin'] +
                    timedelta(days=1)):
                # Prolonge la période actuelle si le jour est consécutif et est aussi une fermeture
                current_period['date_fin'] = js.date
                current_period['ids'].append(js.id)
            else:
                # Commence une nouvelle période de fermeture
                if current_period:  # Ajoute la période précédente si elle existait
                    grouped_jours_speciaux.append(current_period)
                current_period = {
                    'type': 'period_ferme',
                    'date_debut': js.date,
                    'date_fin': js.date,
                    'est_ferme': True,
                    'ids': [js.id]  # Garde une liste des IDs des jours spéciaux individuels qui composent la période
                }
        else:
            # Si le jour spécial n'est pas une fermeture complète
            if current_period:  # Ajoute la période précédente si elle existait
                grouped_jours_speciaux.append(current_period)
            # Ajoute ce jour non-fermé comme un élément individuel
            grouped_jours_speciaux.append({
                'type': 'single_jour',
                'jour_special': js,
                'est_ferme': False,
                # C'est la ligne suivante qui est corrigée :
                'plages_speciales': list(js.plages_specifiques.all())  # <-- CORRIGÉ ICI !
            })
            current_period = None  # Réinitialise la période actuelle

    # Ajoute la dernière période si elle existe
    if current_period:
        grouped_jours_speciaux.append(current_period)

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'grouped_jours_speciaux': grouped_jours_speciaux,  # Nouvelle variable de contexte
    }
    return render(request, 'gestion/salon/jour_special/liste_jours_speciaux.html', context)


@professionnel_required
def ajouter_jour_special(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    if request.method == 'POST':
        form = JourSpecialForm(request.POST, salon=salon)  # Passe le salon au formulaire pour validation
        if form.is_valid():
            jour_special = form.save(commit=False)
            jour_special.salon = salon
            jour_special.save()
            messages.success(request, "✅ Jour spécial ajouté avec succès.")
            return redirect('liste_jours_speciaux', pk=salon.id)
    else:
        form = JourSpecialForm(salon=salon, initial={'date': date.today()})  # Initialise la date à aujourd'hui

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'form': form,
    }
    return render(request, 'gestion/salon/jour_special/ajouter_jour_special.html', context)


@professionnel_required
def modifier_jour_special(request, salon_pk, jour_special_pk):
    salon = get_object_or_404(Salon, pk=salon_pk)
    jour_special = get_object_or_404(JourSpecial, pk=jour_special_pk, salon=salon)

    if request.method == 'POST':
        form = JourSpecialForm(request.POST, instance=jour_special, salon=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Jour spécial modifié avec succès.")
            return redirect('liste_jours_speciaux', pk=salon.id)
    else:
        form = JourSpecialForm(instance=jour_special, salon=salon)

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'form': form,
        'jour_special': jour_special,
    }
    return render(request, 'gestion/salon/jour_special/modifier_jour_special.html', context)


@professionnel_required
def supprimer_jour_special(request, salon_pk, jour_special_pk):
    salon = get_object_or_404(Salon, pk=salon_pk)
    jour_special = get_object_or_404(JourSpecial, pk=jour_special_pk, salon=salon)

    if request.method == 'POST':
        jour_special.delete()
        messages.success(request, "🗑️ Jour spécial supprimé avec succès.")
        return redirect('liste_jours_speciaux', pk=salon.id)

    context = {
        'nom_entreprise': 'Saint Jolie',
        'objet': jour_special,  # Pour le template de confirmation
        'salon': salon,
    }
    return render(request, 'gestion/salon/jour_special/confirmer_suppression_jour_special.html', context)


# --- Vues pour les Plages Horaires Spéciales (liées à un JourSpecial) ---

@professionnel_required
def liste_plages_horaires_speciales(request, salon_pk, jour_special_pk):
    salon = get_object_or_404(Salon, pk=salon_pk)
    jour_special = get_object_or_404(JourSpecial, pk=jour_special_pk, salon=salon)
    plages_speciales = PlageHoraireSpeciale.objects.filter(jour_special=jour_special).order_by('heure_debut')

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'jour_special': jour_special,
        'plages_speciales': plages_speciales,
    }
    return render(request, 'gestion/salon/jour_special/liste_plages_horaires_speciales.html', context)


@professionnel_required
def ajouter_plage_horaire_speciale(request, salon_pk, jour_special_pk):
    salon = get_object_or_404(Salon, pk=salon_pk)
    jour_special = get_object_or_404(JourSpecial, pk=jour_special_pk, salon=salon)

    if request.method == 'POST':
        form = PlageHoraireSpecialeForm(request.POST, jour_special=jour_special)  # Passe le jour_special
        if form.is_valid():
            plage = form.save(commit=False)
            plage.jour_special = jour_special
            plage.save()
            messages.success(request, "✅ Plage horaire spéciale ajoutée.")
            return redirect('liste_plages_horaires_speciales', salon_pk=salon.id, jour_special_pk=jour_special.id)
    else:
        form = PlageHoraireSpecialeForm(jour_special=jour_special)

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'jour_special': jour_special,
        'form': form,
    }
    return render(request, 'gestion/salon/jour_special/ajouter_plage_horaire_speciale.html', context)


@professionnel_required
def modifier_plage_horaire_speciale(request, salon_pk, jour_special_pk, plage_speciale_pk):
    salon = get_object_or_404(Salon, pk=salon_pk)
    jour_special = get_object_or_404(JourSpecial, pk=jour_special_pk, salon=salon)
    plage_speciale = get_object_or_404(PlageHoraireSpeciale, pk=plage_speciale_pk, jour_special=jour_special)

    if request.method == 'POST':
        form = PlageHoraireSpecialeForm(request.POST, instance=plage_speciale, jour_special=jour_special)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Plage horaire spéciale modifiée.")
            return redirect('liste_plages_horaires_speciales', salon_pk=salon.id, jour_special_pk=jour_special.id)
    else:
        form = PlageHoraireSpecialeForm(instance=plage_speciale, jour_special=jour_special)

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'jour_special': jour_special,
        'plage_speciale': plage_speciale,
        'form': form,
    }
    return render(request, 'gestion/salon/jour_special/modifier_plage_horaire_speciale.html', context)


@professionnel_required
def supprimer_plage_horaire_speciale(request, salon_pk, jour_special_pk, plage_speciale_pk):
    salon = get_object_or_404(Salon, pk=salon_pk)
    jour_special = get_object_or_404(JourSpecial, pk=jour_special_pk,
                                     salon=salon)  # <--- maintenant jour_special_pk est défini comme paramètre
    plage_speciale = get_object_or_404(PlageHoraireSpeciale, pk=plage_speciale_pk, jour_special=jour_special)

    if request.method == 'POST':
        plage_speciale.delete()
        messages.success(request, "🗑️ Plage horaire spéciale supprimée.")
        return redirect('liste_plages_horaires_speciales', salon_pk=salon.id, jour_special_pk=jour_special.id)

    context = {
        'nom_entreprise': 'Saint Jolie',
        'objet': plage_speciale,
        'salon': salon,
        'jour_special': jour_special,
    }
    return render(request, 'gestion/salon/jour_special/confirmer_suppression_plage_horaire_speciale.html', context)


@professionnel_required
def ajouter_periode_vacances(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    if request.method == 'POST':
        form = PeriodeVacancesForm(request.POST)  # Utilise le nouveau formulaire
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut']
            date_fin = form.cleaned_data['date_fin']

            current_date = date_debut
            count_added = 0

            while current_date <= date_fin:
                # Vérifier si un JourSpecial existe déjà pour cette date et ce salon
                # afin d'éviter les doublons et de ne pas écraser une configuration existante.
                if not JourSpecial.objects.filter(salon=salon, date=current_date).exists():
                    JourSpecial.objects.create(
                        salon=salon,
                        date=current_date,
                        est_ferme=True  # Toujours fermé pour ce type de période
                    )
                    count_added += 1
                current_date += timedelta(days=1)

            messages.success(request, f"✅ {count_added} jours de fermeture ajoutés pour la période sélectionnée.")
            return redirect('liste_jours_speciaux', pk=salon.id)
    else:
        form = PeriodeVacancesForm()

    context = {
        'nom_entreprise': 'Saint Jolie',
        'salon': salon,
        'form': form,
        'title': "Ajouter une Période de Vacances / Fermeture",
    }
    return render(request, 'gestion/salon/jour_special/ajouter_periode_vacances.html', context)


@professionnel_required
def supprimer_periode_vacances(request, salon_pk):
    salon = get_object_or_404(Salon, pk=salon_pk)
    if request.method == 'POST':
        ids_to_delete_str = request.POST.get('ids_to_delete', '')
        ids_to_delete = [int(id) for id in ids_to_delete_str.split(',') if id]

        # Vérification de sécurité
        jours_speciaux_a_supprimer = JourSpecial.objects.filter(id__in=ids_to_delete, salon=salon)

        if jours_speciaux_a_supprimer.count() == len(ids_to_delete):
            jours_speciaux_a_supprimer.delete()
            messages.success(request, "La période de fermeture a été supprimée avec succès.")
        else:
            messages.error(request, "Erreur lors de la suppression de la période.")

    return redirect('liste_jours_speciaux', pk=salon_pk)


@professionnel_required
def supprimer_jours_speciaux_multiples(request, salon_pk):
    if request.method == 'POST':
        salon = get_object_or_404(Salon, pk=salon_pk)
        ids_to_delete_str = request.POST.get('ids_to_delete', '')
        ids_to_delete = [int(id_str) for id_str in ids_to_delete_str.split(',') if id_str.strip()]

        if ids_to_delete:
            # S'assurer que les jours spéciaux appartiennent bien au salon
            jours_a_supprimer = JourSpecial.objects.filter(salon=salon, id__in=ids_to_delete)
            count_deleted, _ = jours_a_supprimer.delete()
            messages.success(request, f"🗑️ {count_deleted} jours spéciaux supprimés avec succès.")
        else:
            messages.error(request, "Aucun jour spécial sélectionné pour la suppression.")

        return redirect('liste_jours_speciaux', pk=salon.id)
    return redirect('liste_jours_speciaux', pk=salon_pk)  # Rediriger si ce n'est pas un POST
