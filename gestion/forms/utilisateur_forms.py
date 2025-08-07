# gestion/forms/utilisateur_forms.py

from django import forms
from gestion.models import Utilisateur
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class UtilisateurCreationForm(UserCreationForm):
    """
    Formulaire pour la création d'un nouvel utilisateur.
    Il inclut le champ 'telephone' et utilise les fonctionnalités
    natives de UserCreationForm pour la gestion des mots de passe.
    """

    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'date_de_naissance',
            'telephone',
            'role',
            'is_active',
        )
        labels = {
            'email': _('Adresse e-mail (Identifiant de connexion)'),
            'username': _('Nom d\'utilisateur'),
            'first_name': _('Prénom'),
            'last_name': _('Nom (de famille)'),
            'date_de_naissance': _('Date de naissance'),
            'telephone': _('Numéro de téléphone'),
            'role': _('Rôle de l\'utilisateur'),
            'is_active': _('Est Actif'),
        }
        widgets = {
            'date_de_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'username': _('Obligatoire. 150 caractères ou moins. Lettres, chiffres et @/.+/-/_ seulement.'),
            'is_active': _(
                'Indique si le compte utilisateur doit être traité comme actif. Décochez ceci au lieu de supprimer '
                'les comptes.'),
            'telephone': _('Entrez un numéro de téléphone valide (ex: +324701234567, 0471 23 45 67).')
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Cette adresse e-mail est déjà utilisée."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == 'professionnel':
            user.is_staff = True
        else:
            user.is_staff = False
        if commit:
            user.save()
        return user


class UtilisateurChangeForm(UserChangeForm):
    """
    Formulaire pour la modification des informations d'un utilisateur existant.
    Il inclut le champ 'telephone'.
    IMPORTANT : Ce formulaire n'est PAS destiné à changer le mot de passe.
    Les champs de mot de passe sont exclus pour éviter les problèmes de hashage.
    """

    class Meta(UserChangeForm.Meta):
        model = Utilisateur
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'date_de_naissance',
            'telephone',
            'role',
            'is_active',
        )

        labels = {
            'email': _('Adresse e-mail (Identifiant de connexion)'),
            'username': _('Nom d\'utilisateur'),
            'first_name': _('Prénom'),
            'last_name': _('Nom (de famille)'),
            'date_de_naissance': _('Date de naissance'),
            'telephone': _('Numéro de téléphone'),
            'role': _('Rôle de l\'utilisateur'),
            'is_active': _('Est Actif'),

        }
        widgets = {
            'date_de_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }
        help_texts = {
            'username': _('Obligatoire. 150 caractères ou moins. Lettres, chiffres et @/.+/-/_ seulement.'),
            'is_active': _(
                'Indique si le compte utilisateur doit être traité comme actif. Décochez ceci au lieu de supprimer '
                'les comptes.'),
            'telephone': _('Entrez un numéro de téléphone valide (ex: +324701234567, 0471 23 45 67).')

        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.instance.pk:  # Lors d'une modification
            if Utilisateur.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(_("Cette adresse e-mail est déjà utilisée par un autre compte."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == 'professionnel':
            user.is_staff = True
        else:
            user.is_staff = False

        if commit:
            user.save()
        return user


class UtilisateurPublicRegistrationForm(UserCreationForm):
    """
    Formulaire simplifié pour l'inscription d'un nouvel utilisateur (client/élève) via la page "Créer un compte".
    Expose les champs pertinents pour l'utilisateur final et définit le rôle/statut par défaut.
    """

    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'date_de_naissance',
            'telephone',
        )
        labels = {
            'email': _('Adresse e-mail (Identifiant de connexion)'),
            'username': _('Nom d\'utilisateur'),
            'first_name': _('Prénom'),
            'last_name': _('Nom (de famille)'),
            'date_de_naissance': _('Date de naissance'),
            'telephone': _('Numéro de téléphone'),
        }
        widgets = {
            'date_de_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'username': _('Obligatoire. 150 caractères ou moins. Lettres, chiffres et @/.+/-/_ seulement.'),
            'telephone': _('Entrez un numéro de téléphone valide (ex: +324701234567, 0471 23 45 67).')
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Cette adresse e-mail est déjà utilisée."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        user.is_staff = False
        user.is_active = True
        if commit:
            user.save()
        return user
