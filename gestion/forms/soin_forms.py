# gestion/forms/soin_forms.py

from django import forms
from gestion.models import Soin, SoinSalonDetail
from datetime import timedelta


class SoinForm(forms.ModelForm):
    class Meta:
        model = Soin
        fields = ['type_de_soin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type_de_soin'].label = "Type de Soin"


class SoinSalonDetailForm(forms.ModelForm):
    duree_minutes = forms.IntegerField(
        label="Durée (en minutes)",
        min_value=1,
        max_value=360,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 60'}),
        required=True
    )

    class Meta:
        model = SoinSalonDetail
        fields = ['soin', 'salon', 'prix', 'commentaire_specifique']
        labels = {
            'soin': 'Type de Soin Général',
            'salon': 'Salon Associé',
            'prix': 'Prix du Soin (pour ce salon)',
            'commentaire_specifique': 'Commentaire (spécifique à ce soin pour ce salon)',
        }
        widgets = {
            'commentaire_specifique': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'salon': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['soin'].queryset = Soin.objects.all()

        self.fields['soin'].widget.attrs.update({'class': 'form-control'})
        self.fields['prix'].widget.attrs.update({'class': 'form-control'})

        if self.instance and self.instance.duree:
            self.initial['duree_minutes'] = int(self.instance.duree.total_seconds() / 60)

    def clean(self):
        cleaned_data = super().clean()
        duree_minutes = cleaned_data.get('duree_minutes')

        if duree_minutes is not None:
            cleaned_data['duree'] = timedelta(minutes=duree_minutes)
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.duree = self.cleaned_data['duree']
        if commit:
            instance.save()
        return instance
