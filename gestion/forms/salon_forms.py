# gestion/forms/salon_forms.py

from django import forms
from gestion.models import Salon


class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = [
            'nom',
            'nombre_employes',
            'adresse',
            'telephone',
            'email',
            'date_debut_periode',
            'date_fin_periode',
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_employes': forms.NumberInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +32470123456'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: contact@salon.com'}),
            'date_debut_periode': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'date_fin_periode': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }
        labels = {
            'nom': 'Nom du Salon',
            'nombre_employes': 'Nombre d\'Employés',
            'adresse': 'Adresse',
            'telephone': 'Numéro de Téléphone',
            'email': 'Adresse E-mail du Salon',
            'date_debut_periode': 'Début de la période d\'activité (optionnel)',
            'date_fin_periode': 'Fin de la période d\'activité (optionnel)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                field.widget.attrs.update({'class': 'form-control'})

        # Ajout des formats de date pour la prise en charge de différents formats
        self.fields['date_debut_periode'].input_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        self.fields['date_fin_periode'].input_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
