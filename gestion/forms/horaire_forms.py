# gestion/forms/horaire_forms.py

from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from gestion.models import PlageHoraire, Jour, JourSpecial, PlageHoraireSpeciale


class PlageHoraireForm(forms.ModelForm):
    class Meta:
        model = PlageHoraire
        fields = ['jour', 'heure_debut', 'heure_fin']
        widgets = {
            'jour': forms.Select(attrs={'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
        labels = {
            'jour': 'Jour de la semaine',
            'heure_debut': 'Heure de début',
            'heure_fin': 'Heure de fin',
        }

    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        self.fields['jour'].queryset = Jour.objects.all().order_by('numero')

        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        jour = cleaned_data.get('jour')
        salon = self.salon

        if not all([jour, salon, heure_debut, heure_fin]):
            # Si une des données est manquante, on arrête la validation
            # car elle a déjà été gérée par les champs obligatoires.
            return cleaned_data

        # --- NOUVELLE LOGIQUE DE VALIDATION : COHÉRENCE JOUR / PÉRIODE D'ACTIVITÉ ---
        date_debut_periode = salon.date_debut_periode
        date_fin_periode = salon.date_fin_periode

        if date_debut_periode and date_fin_periode:
            # On trouve le jour de la semaine du début de la période
            jour_debut_periode_weekday = date_debut_periode.weekday()
            # On trouve le jour de la semaine de la fin de la période
            jour_fin_periode_weekday = date_fin_periode.weekday()
            # On récupère le numéro du jour de la semaine du formulaire
            numero_jour_form = jour.numero

            # Vérifie si le jour du formulaire est en dehors de l'intervalle de la période
            if not (jour_debut_periode_weekday <= numero_jour_form <= jour_fin_periode_weekday):
                # Il y a un cas spécial si la période se termine la semaine suivante
                # ex: jeudi -> lundi (5 jours)
                if jour_debut_periode_weekday > jour_fin_periode_weekday:
                    # Dans ce cas, le jour du formulaire doit être >= jour de début OU <= jour de fin
                    if not (
                            numero_jour_form >= jour_debut_periode_weekday or
                            numero_jour_form <= jour_fin_periode_weekday):
                        raise ValidationError(
                            "Le jour sélectionné n'est pas inclus dans la période d'activité du salon. "
                            "Veuillez choisir "
                            "un autre jour ou ajuster la période d'activité.")
                else:
                    # Cas normal : la période se déroule dans la même semaine
                    if not (
                            jour_debut_periode_weekday <= numero_jour_form <= jour_fin_periode_weekday):
                        raise ValidationError(
                            "Le jour sélectionné n'est pas inclus dans la période d'activité du salon. "
                            "Veuillez choisir "
                            "un autre jour ou ajuster la période d'activité.")

        # --- FIN DE LA NOUVELLE LOGIQUE ---

        if heure_debut and heure_fin:
            if heure_fin <= heure_debut:
                raise ValidationError(_("L'heure de fin doit être postérieure à l'heure de début."))

        if jour and heure_debut and heure_fin and salon:
            qs = PlageHoraire.objects.filter(salon=salon, jour=jour)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            overlapping_plages = qs.filter(
                heure_debut__lt=heure_fin,
                heure_fin__gt=heure_debut
            )

            if overlapping_plages.exists():
                raise ValidationError(_("Cette plage horaire chevauche une plage existante pour ce jour et ce salon."))

        return cleaned_data


class JourSpecialForm(forms.ModelForm):
    class Meta:
        model = JourSpecial
        fields = ['date', 'est_ferme']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'est_ferme': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'date': 'Date spéciale',
            'est_ferme': 'Le salon est-il entièrement fermé ce jour-là ?',
        }

    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        date_speciale = cleaned_data.get('date')
        salon = self.salon

        if date_speciale and salon:
            qs = JourSpecial.objects.filter(salon=salon, date=date_speciale)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError(
                    {'date': _("Un jour spécial pour cette date existe déjà pour ce salon.")}
                )
        return cleaned_data


class PlageHoraireSpecialeForm(forms.ModelForm):
    class Meta:
        model = PlageHoraireSpeciale
        fields = ['heure_debut', 'heure_fin']
        widgets = {
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
        labels = {
            'heure_debut': 'Heure de début',
            'heure_fin': 'Heure de fin',
        }

    def __init__(self, *args, **kwargs):
        self.jour_special = kwargs.pop('jour_special', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        jour_special = self.jour_special

        if heure_debut and heure_fin:
            if heure_fin <= heure_debut:
                raise ValidationError(_("L'heure de fin doit être postérieure à l'heure de début."))

        if jour_special and heure_debut and heure_fin:
            qs = PlageHoraireSpeciale.objects.filter(jour_special=jour_special)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            overlapping_plages = qs.filter(
                heure_debut__lt=heure_fin,
                heure_fin__gt=heure_debut
            )
            if overlapping_plages.exists():
                raise ValidationError(_("Cette plage horaire chevauche une plage existante pour ce jour spécial."))

        return cleaned_data


class PeriodeVacancesForm(forms.Form):
    date_debut = forms.DateField(
        label="Date de début de la période",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=date.today  # Pré-remplit avec la date du jour
    )
    date_fin = forms.DateField(
        label="Date de fin de la période",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False  # Laisser optionnel si on veut fermer juste un jour avec ce formulaire
    )
    # Pour s'assurer que cette période est toujours une fermeture complète
    est_ferme = forms.BooleanField(
        label="Fermeture complète pendant cette période",
        initial=True,
        required=False,  # Pour qu'il puisse être coché ou non
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        est_ferme = cleaned_data.get('est_ferme')  # On récupère la valeur pour l'utiliser

        if date_debut and date_fin:
            if date_fin < date_debut:
                self.add_error('date_fin', _("La date de fin doit être postérieure ou égale à la date de début."))
        elif date_debut and not date_fin:
            # Si seule date_debut est spécifiée, c'est une fermeture d'un seul jour.
            # On peut forcer date_fin à être date_debut pour simplifier le traitement derrière.
            cleaned_data['date_fin'] = date_debut

        if not est_ferme:
            # Si "Fermeture complète" n'est pas coché, cela signifie que le but est de définir des
            # horaires spéciaux. Or, ce formulaire n'est pas fait pour ça.
            # On pourrait envisager d'ajouter un champ pour "Type de période : Fermeture ou Horaires Spécifiques".
            # Pour l'instant, on se concentre sur la fermeture comme demandé "vacances".
            # Je lève une erreur si ce n'est pas une fermeture, pour garder le formulaire simple.
            raise ValidationError(("Ce formulaire est destiné à la gestion des périodes de fermeture. Pour des "
                                   "horaires spécifiques, veuillez ajouter un 'Jour Spécial' et ses plages horaires."),
                                  code='not_a_full_closure'
                                  )

        return cleaned_data
