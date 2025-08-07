# gestion/models.py

from datetime import time, date, datetime, timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Définition du RegexValidator pour les numéros de téléphone européens
phone_regex = RegexValidator(
    regex=r'^\+?[\d\s\-\(\)]{7,15}$',
    message="Le numéro de téléphone doit être entré au format: '+999999999'. "
            "Il peut inclure des espaces, des tirets ou des parenthèses. Minimum 7 chiffres, maximum 15."
)


class Utilisateur(AbstractUser):
    # AbstractUser fournit déjà :
    # username
    # first_name
    # last_name
    # email
    # password
    # is_staff (utilisé pour déterminer si c'est un 'professionnel')
    # is_active

    email = models.EmailField(unique=True, blank=False, null=False)
    date_de_naissance = models.DateField(null=True, blank=True)

    telephone = models.CharField(
        validators=[phone_regex],
        max_length=20,
        null=True,
        blank=True,
        unique=True
    )

    ROLE_CHOICES = [
        ('client', 'Client'),
        ('professionnel', 'Professionnel'),
        ('eleve', 'Élève'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    # Définis l'email comme champ de connexion principal
    USERNAME_FIELD = 'email'
    # Champs requis lors de la création d'un superutilisateur (en plus de l'email et du mot de passe)
    # Important : 'username' reste requis ici même si vous utilisez email comme USERNAME_FIELD
    # C'est une particularité de AbstractUser. Si vous ne voulez pas de username,
    # il faudrait utiliser AbstractBaseUser, mais c'est plus complexe.
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        # Utilise les noms de champs de AbstractUser et ajoute le rôle
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

    # --- DÉBUT MODIFICATION : AJOUT DES PROPRIÉTÉS POUR LES RÔLES ---
    @property
    def is_client(self):
        """Retourne True si l'utilisateur est un client."""
        return self.role == 'client'

    @property
    def is_eleve(self):
        """Retourne True si l'utilisateur est un élève."""
        return self.role == 'eleve'

    @property
    def is_professional(self):
        """
        Retourne True si l'utilisateur est un professionnel.
        La détermination est basée sur le champ 'role'.
        """
        return self.role == 'professionnel'


class Soin(models.Model):
    type_de_soin = models.CharField(max_length=100)
    salons = models.ManyToManyField("Salon", through='SoinSalonDetail', related_name="soins_offerts_details")

    def __str__(self):
        return f"{self.type_de_soin}"


class Salon(models.Model):
    nom = models.CharField(max_length=100)
    nombre_employes = models.PositiveIntegerField(default=0)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # --- NOUVEAUX CHAMPS AJOUTÉS ---
    date_debut_periode = models.DateField(
        null=True,
        blank=True,
        verbose_name="Début de la période d'activité"
    )
    date_fin_periode = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fin de la période d'activité"
    )

    def __str__(self):
        return self.nom

    @property
    def get_jours_ouverture_from_plages(self):
        jours_ouverts = self.plages_horaires.values_list('jour__nom', 'jour__numero').distinct()
        jours_ouverts_list = sorted(list(jours_ouverts), key=lambda x: x[1])
        return [jour_name for jour_name, _ in jours_ouverts_list]


class SoinSalonDetail(models.Model):
    soin = models.ForeignKey(Soin, on_delete=models.CASCADE)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    commentaire_specifique = models.TextField(blank=True, verbose_name="Commentaire spécifique au salon")
    duree = models.DurationField()

    class Meta:
        unique_together = ('soin', 'salon')

    def __str__(self):
        if self.commentaire_specifique:
            return (f"{self.soin.type_de_soin} chez {self.salon.nom} - "
                    f"Prix: {self.prix}€ - Commentaire: {self.commentaire_specifique}")
        else:
            return f"{self.soin.type_de_soin} chez {self.salon.nom} - Prix: {self.prix}€"


class Jour(models.Model):
    JOUR_CHOICES = [
        (0, 'Lundi'), (1, 'Mardi'), (2, 'Mercredi'), (3, 'Jeudi'),
        (4, 'Vendredi'), (5, 'Samedi'), (6, 'Dimanche'),
    ]

    nom = models.CharField(max_length=20, unique=True, null=True, blank=True)
    numero = models.PositiveIntegerField(choices=JOUR_CHOICES, unique=True)

    def save(self, *args, **kwargs):
        if not self.nom and self.numero is not None:
            self.nom = dict(self.JOUR_CHOICES).get(self.numero, "Jour inconnu")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom if self.nom else dict(self.JOUR_CHOICES).get(self.numero, "Jour inconnu (sans nom)")

    class Meta:
        ordering = ['numero']


class JourSpecial(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='jours_speciaux')
    date = models.DateField()
    heure_ouverture = models.TimeField(null=True, blank=True)
    heure_fermeture = models.TimeField(null=True, blank=True)
    est_ferme = models.BooleanField(default=False)

    class Meta:
        unique_together = ('salon', 'date')

    def __str__(self):
        if self.est_ferme:
            return f"{self.date} - Fermé"
        if self.heure_ouverture and self.heure_fermeture:
            return f"{self.date} - {self.heure_ouverture.strftime('%H:%M')} à {self.heure_fermeture.strftime('%H:%M')}"
        return f"{self.date} - Horaires non définis (sera considéré comme fermé si aucune plage spéciale n'est définie)"


class PlageHoraire(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='plages_horaires')
    jour = models.ForeignKey(Jour, on_delete=models.CASCADE)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    class Meta:
        unique_together = ('salon', 'jour', 'heure_debut', 'heure_fin')

    def __str__(self):
        return (f"{self.salon.nom} - {self.jour.nom} : {self.heure_debut.strftime('%H:%M')} - "
                f"{self.heure_fin.strftime('%H:%M')}")


class PlageHoraireSpeciale(models.Model):
    jour_special = models.ForeignKey(JourSpecial, on_delete=models.CASCADE,
                                     related_name='plages_specifiques')
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    class Meta:
        unique_together = ('jour_special', 'heure_debut', 'heure_fin')

    def __str__(self):
        return (f"Jour spécial {self.jour_special.date} : {self.heure_debut.strftime('%H:%M')} - "
                f"{self.heure_fin.strftime('%H:%M')}")


STATUT_CHOICES = [
    ('prévu', 'Prévu'),
    ('terminé', 'Terminé'),
    ('annulé', 'Annulé'),
]


class RendezVous(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    soin_detail = models.ForeignKey(SoinSalonDetail, on_delete=models.CASCADE, verbose_name="Soin Spécifique au Salon")

    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)

    def __str__(self):
        return (f"RDV {self.utilisateur.first_name} {self.utilisateur.last_name} - "  # Utilise first_name/last_name
                f"{self.soin_detail.soin.type_de_soin} ({self.date} à {self.heure_debut.strftime('%H:%M')})")
