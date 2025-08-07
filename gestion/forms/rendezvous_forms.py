# gestion/forms/rendezvous_forms.py

from django import forms
from gestion.models import (
    Soin, SoinSalonDetail, Salon, RendezVous, Utilisateur, Jour, PlageHoraire,
    JourSpecial, PlageHoraireSpeciale
)
from django.core.exceptions import ValidationError
from datetime import timedelta, datetime, time, date


class RendezVousForm(forms.ModelForm):
    utilisateur = forms.ModelChoiceField(
        queryset=Utilisateur.objects.none(),
        label="Bénéficiaire du soin",
        empty_label="Sélectionner un bénéficiaire",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    heure_debut = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))

    soin_detail = forms.ModelChoiceField(
        queryset=SoinSalonDetail.objects.none(),
        label="Type de Soin",
        empty_label="Sélectionner un soin",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = RendezVous
        fields = ['utilisateur', 'soin_detail', 'date', 'heure_debut', 'statut']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.salon = kwargs.pop('salon', None)
        self.for_self_appointment = kwargs.pop('for_self_appointment', False)

        super().__init__(*args, **kwargs)

        # --- DÉBUT DES MODIFICATIONS ---
        # GESTION DU CHAMP 'utilisateur'
        # La condition est modifiée pour que les professionnels et les élèves voient le même champ.
        if self.for_self_appointment:
            self.fields['utilisateur'].widget = forms.HiddenInput()
            self.fields['utilisateur'].required = False
            self.fields['utilisateur'].label = ""
            if self.user:
                self.fields['utilisateur'].initial = self.user.pk
                self.fields['utilisateur'].queryset = Utilisateur.objects.filter(pk=self.user.pk)
        elif self.user and (self.user.is_professional or self.user.role == 'eleve'):
            self.fields['utilisateur'].queryset = Utilisateur.objects.all().order_by('last_name', 'first_name')
            self.fields['utilisateur'].empty_label = "Sélectionner un bénéficiaire"
        else:
            self.fields['utilisateur'].queryset = Utilisateur.objects.none()

        # GESTION DU CHAMP 'statut'
        # La condition est modifiée pour que le champ "statut" ne soit caché que pour la prise de rendez-vous
        # personnelle.
        if self.for_self_appointment:
            self.fields['statut'].widget = forms.HiddenInput()
            self.fields['statut'].initial = 'prévu'
            self.fields['statut'].required = False
        else:
            self.fields['statut'].initial = 'prévu'
        # --- FIN DES MODIFICATIONS ---

        # GESTION DU CHAMP 'soin_detail'
        if self.salon:
            self.fields['soin_detail'].queryset = SoinSalonDetail.objects.filter(salon=self.salon).select_related(
                'soin')
            self.fields['soin_detail'].label_from_instance = lambda \
                obj: f"{obj.soin.type_de_soin} ({int(obj.duree.total_seconds() / 60)} min) - {obj.prix}€"
        else:
            self.fields['soin_detail'].queryset = SoinSalonDetail.objects.none()

        # GESTION DES VALEURS INITIALES LORS DE LA MODIFICATION D'UN RV
        if self.instance and self.instance.pk:
            self.fields['date'].initial = self.instance.date
            self.fields['heure_debut'].initial = self.instance.heure_debut

    def clean(self):
        cleaned_data = super().clean()

        utilisateur_rv = cleaned_data.get('utilisateur')
        if self.for_self_appointment and self.user:
            utilisateur_rv = self.user
            if not cleaned_data.get('utilisateur'):
                cleaned_data['utilisateur'] = self.user

        date_rv = cleaned_data.get('date')
        heure_debut_rv = cleaned_data.get('heure_debut')
        soin_detail = cleaned_data.get('soin_detail')
        salon = self.salon

        if not all([utilisateur_rv, date_rv, heure_debut_rv, soin_detail, salon]):
            return cleaned_data

        # --- NOUVELLE LOGIQUE DE VALIDATION POUR LA PÉRIODE D'ACTIVITÉ ---
        if salon.date_debut_periode and date_rv < salon.date_debut_periode:
            raise ValidationError("Le salon n'est pas encore en période d'activité à cette date.")

        if salon.date_fin_periode and date_rv > salon.date_fin_periode:
            raise ValidationError("Le salon ne sera plus en période d'activité à cette date.")
        # --- FIN DE LA NOUVELLE LOGIQUE ---

        rv_datetime_debut = datetime.combine(date_rv, heure_debut_rv)
        if rv_datetime_debut < datetime.now():
            raise ValidationError("Le rendez-vous ne peut pas être pris dans le passé.")

        duree_soin = soin_detail.duree
        duree_totale_rv = duree_soin + timedelta(minutes=10)
        dt_heure_fin_rv = datetime.combine(datetime.min.date(), heure_debut_rv) + duree_totale_rv
        heure_fin_rv = dt_heure_fin_rv.time()
        cleaned_data['heure_fin'] = heure_fin_rv

        # Validation : heures d'ouverture du salon
        jour_semaine = date_rv.weekday()
        jour_special = JourSpecial.objects.filter(salon=salon, date=date_rv).first()
        plages_ouverture_effectives = []
        if jour_special:
            if jour_special.est_ferme:
                raise ValidationError("Le salon est entièrement fermé ce jour spécial.")
            plages_ouverture_effectives = PlageHoraireSpeciale.objects.filter(jour_special=jour_special).order_by(
                'heure_debut')
        else:
            try:
                jour_obj = Jour.objects.get(numero=jour_semaine)
                plages_ouverture_effectives = PlageHoraire.objects.filter(salon=salon, jour=jour_obj).order_by(
                    'heure_debut')
            except Jour.DoesNotExist:
                pass

        if not any(
                plage.heure_debut <= heure_debut_rv and plage.heure_fin >= heure_fin_rv
                for plage in plages_ouverture_effectives
        ):
            raise ValidationError(
                f"Le rendez-vous ({heure_debut_rv.strftime('%H:%M')} - {heure_fin_rv.strftime('%H:%M')}) "
                "n'est pas entièrement compris dans les heures d'ouverture du salon pour cette date."
            )

        # Validation 1: Pas de chevauchement pour le client
        qs_existing_rv_client = RendezVous.objects.filter(
            utilisateur=utilisateur_rv,
            date=date_rv,
            heure_debut__lt=heure_fin_rv,
            heure_fin__gt=heure_debut_rv,
        )
        if self.instance and self.instance.pk:
            qs_existing_rv_client = qs_existing_rv_client.exclude(pk=self.instance.pk)
        if qs_existing_rv_client.exists():
            raise ValidationError(
                "Ce client a déjà un rendez-vous qui chevauche cette plage horaire. "
                "Veuillez choisir un autre créneau."
            )

        # Validation 2: Disponibilité des employés du salon
        qs_existing_rv_salon = RendezVous.objects.filter(
            salon=salon,
            date=date_rv,
            heure_debut__lt=heure_fin_rv,
            heure_fin__gt=heure_debut_rv,
        )
        if self.instance and self.instance.pk:
            qs_existing_rv_salon = qs_existing_rv_salon.exclude(pk=self.instance.pk)

        nombre_employes_occupes = qs_existing_rv_salon.count()
        nombre_employes_total = salon.nombre_employes

        if nombre_employes_total <= 0:
            raise ValidationError("Ce salon ne dispose pas d'employés enregistrés pour prendre des rendez-vous.")

        if nombre_employes_occupes >= nombre_employes_total:
            raise ValidationError(
                "Désolé, tous les employés sont occupés à cette heure. Veuillez choisir un autre créneau.")

        return cleaned_data
