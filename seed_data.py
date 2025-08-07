import os
import django
import random
from datetime import timedelta, date, time  # Ajout de 'time' pour les heures

# Configuration de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GestionClient.settings")
django.setup()

from django.contrib.auth.hashers import make_password

# Assure-toi d'importer tous les modèles nécessaires
# Ajout de JourSpecial et PlageHoraireSpeciale
from gestion.models import Utilisateur, Soin, Salon, SoinSalonDetail, Jour, \
    RendezVous, PlageHoraire, JourSpecial, PlageHoraireSpeciale

# --- Données de base ---
prenoms = ['Alice', 'Bob', 'Chloé', 'David', 'Eva', 'Félix', 'Gina', 'Hugo',
           'Iris', 'Julien']
noms = ['Dupont', 'Martin', 'Durand', 'Petit', 'Moreau', 'Garcia', 'Lemoine',
        'Faure', 'Henry', 'Lopez']

# --- NOUVELLE LISTE POUR LES NUMÉROS DE TÉLÉPHONE BELGES ---
# Exemples de préfixes pour numéros de mobile belges (04xx)
prefixes_mobiles = ["047", "048", "049"]
# Exemples de préfixes pour numéros de fixe belges (0xx)
prefixes_fixes = ["02", "03", "04", "071", "081", "087"]  # Bruxelles, Anvers, Liège, Charleroi, Namur, Verviers
# -----------------------------------------------------------

types_de_soins_base = [  # Ce sont les types de soins GÉNÉRAUX
    {'nom': 'Massage Relaxant', 'duree_min': 60},
    {'nom': 'Soin du Visage Hydratant', 'duree_min': 90},
    {'nom': 'Manucure Classique', 'duree_min': 45},
    {'nom': 'Pédicure Complète', 'duree_min': 75},
    {'nom': 'Épilation Jambes Complètes', 'duree_min': 30},
    {'nom': 'Réflexologie Plantaire', 'duree_min': 60},
    {'nom': 'Peeling Doux', 'duree_min': 45},
    {'nom': 'Soin Anti-Âge Premium', 'duree_min': 120},
    {'nom': 'Gommage Corporel', 'duree_min': 30},
    {'nom': 'Coiffure Coupe & Brushing', 'duree_min': 60},
]


# --- Fonctions utilitaires pour générer des numéros belges ---
def generate_belgian_mobile_number():
    prefix = random.choice(prefixes_mobiles)
    # 7 chiffres après le préfixe
    # Format 04XX XXX XXX
    return f"{prefix} {random.randint(100, 999)} {random.randint(100, 999)}"


def generate_belgian_fixed_number():
    prefix = random.choice(prefixes_fixes)
    if prefix in ["02", "03", "04"]:  # Numéros à 8 chiffres après le préfixe (pour Liège, Bruxelles, Anvers)
        # Format 0X XXX XX XX (ex: 04 366 84 70)
        return f"{prefix} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
    else:  # Numéros à 9 chiffres après le préfixe (pour Charleroi, Namur, Verviers)
        # Format 0XXX XX XX XX (ex: 081 12 34 56)
        return f"{prefix} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"


def generate_random_belgian_phone_number():
    if random.random() < 0.7:  # 70% de chance d'avoir un mobile
        return generate_belgian_mobile_number()
    else:  # 30% de chance d'avoir un fixe
        return generate_belgian_fixed_number()


# -------------------------------------------------------------

# --- Nettoyage complet pour un "fresh start" ---
print("🧹 Suppression des données existantes (rendez-vous, plages_speciales, jours_speciaux, plages_horaires, "
      "soins_detail, soins, salons, utilisateurs)...")

RendezVous.objects.all().delete()
PlageHoraireSpeciale.objects.all().delete()
JourSpecial.objects.all().delete()
PlageHoraire.objects.all().delete()
SoinSalonDetail.objects.all().delete()
Soin.objects.all().delete()
Salon.objects.all().delete()
Utilisateur.objects.all().delete()
Jour.objects.all().delete()

print("Nettoyage terminé.")

# --- Création des utilisateurs ---
# Pour l'utilisateur 'jonathan lacourt'
# Il est superutilisateur et staff, il aura donc accès à l'admin et sera considéré comme "professionnel"
u = Utilisateur(
    username="jonathan.lacourt",
    first_name="jonathan",
    last_name="lacourt",
    email="jonjonlacourt@live.be",
    is_staff=True,
    is_superuser=True,
    # Définir le rôle explicitement pour Jonathan
    role='professionnel',  # <--- AJOUT : Définir le rôle pour Jonathan
    date_de_naissance=date(1983, 2, 9),
    telephone=generate_random_belgian_phone_number()
)
u.set_password("lacourt")
u.save()
print("Utilisateur 'jonathan lacourt' (professionnel) créé.")

# Pour les 10 utilisateurs de test
for i in range(10):
    user_role_type = random.choice(['client', 'professionnel', 'eleve'])  # Ajout de 'eleve' pour varier les rôles
    Utilisateur.objects.create(
        username=f"user{i}",
        first_name=random.choice(prenoms),
        last_name=random.choice(noms),
        email=f"user{i}@exemple.com",
        password=make_password("mdp"),
        # Le champ 'role' est maintenant le maître des propriétés is_client, is_professional, is_eleve
        role=user_role_type,  # <--- MODIFICATION ICI
        # is_staff devrait être True si l'utilisateur doit aussi avoir accès à l'administration Django
        # Pour les utilisateurs de test, mettez is_staff à True seulement si le rôle est 'professionnel'
        is_staff=(user_role_type == 'professionnel'),  # <--- MODIFICATION ICI : is_staff basé sur le rôle
        date_de_naissance=date(1990 + i, random.randint(1, 12), random.randint(1, 28)),
        telephone=generate_random_belgian_phone_number()
    )
print("10 utilisateurs de test (clients, professionnels et élèves) créés.")

# --- Création des Jours de la semaine ---
jours_semaine_map = {
    'Lundi': 0, 'Mardi': 1, 'Mercredi': 2, 'Jeudi': 3,
    'Vendredi': 4, 'Samedi': 5, 'Dimanche': 6
}
jours_objets = {}
print("\nCréation des Jours de la semaine...")
for nom_jour, numero in jours_semaine_map.items():
    jour_obj, created = Jour.objects.get_or_create(nom=nom_jour, numero=numero)
    jours_objets[nom_jour] = jour_obj
    if created:
        print(f"Jour '{nom_jour}' créé.")

# --- Création des salons et de leurs plages horaires régulières ---
print("\nCréation des salons et de leurs plages horaires régulières...")

# Salon 1: Le Spa Zen (Namur)
salon1 = Salon.objects.create(
    nom="Le Spa Zen (Namur)",
    adresse="123 Rue de la Sérénité, 5000 Namur",
    telephone="081123456",
    email="contact@spazen.com",
    nombre_employes=5,
)
print(f"Salon '{salon1.nom}' créé.")

# Plages horaires pour Le Spa Zen (Namur)
jours_ouv_spa_zen = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
for jour_nom in jours_ouv_spa_zen:
    jour_obj = jours_objets[jour_nom]
    PlageHoraire.objects.create(
        salon=salon1,
        jour=jour_obj,
        heure_debut=time(9, 0),
        heure_fin=time(12, 0)
    )
    PlageHoraire.objects.create(
        salon=salon1,
        jour=jour_obj,
        heure_debut=time(13, 0),
        heure_fin=time(18, 0)
    )
print(f"  -> Plages horaires régulières ajoutées pour '{salon1.nom}'.")

# Ajout d'un jour spécial de fermeture pour Le Spa Zen (ex: Noël prochain)
jour_noel = date(2025, 12, 25)  # Adaptez l'année si besoin
jour_special_ferme_spa_zen, created = JourSpecial.objects.get_or_create(
    salon=salon1,
    date=jour_noel,
    defaults={'est_ferme': True}
)
if created:
    print(f"  -> Jour Spécial de fermeture ({jour_noel}) créé pour '{salon1.nom}'.")

# Salon 2: Beauté Divine (Liège)
salon2 = Salon.objects.create(
    nom="Beauté Divine (Liège)",
    adresse="45 Avenue de la Gloire, 4000 Liège",
    telephone="041987654",
    email="info@beautedivine.com",
    nombre_employes=3,
)
print(f"Salon '{salon2.nom}' créé.")

# Plages horaires pour Beauté Divine (Liège)
jours_ouv_beaute_divine = ['Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
for jour_nom in jours_ouv_beaute_divine:
    jour_obj = jours_objets[jour_nom]
    PlageHoraire.objects.create(
        salon=salon2,
        jour=jour_obj,
        heure_debut=time(10, 0),
        heure_fin=time(14, 0)
    )
    PlageHoraire.objects.create(
        salon=salon2,
        jour=jour_obj,
        heure_debut=time(15, 0),
        heure_fin=time(19, 0)
    )
print(f"  -> Plages horaires régulières ajoutées pour '{salon2.nom}'.")

# Ajout d'un jour spécial avec horaires réduits pour Beauté Divine (ex: veille de nouvel an)
jour_nouvel_an = date(2025, 12, 31)  # Adaptez l'année si besoin
jour_special_partiel_beaute_divine, created = JourSpecial.objects.get_or_create(
    salon=salon2,
    date=jour_nouvel_an,
    defaults={'est_ferme': False}
)
if created:
    print(f"  -> Jour Spécial avec horaires réduits ({jour_nouvel_an}) créé pour '{salon2.nom}'.")
    PlageHoraireSpeciale.objects.create(
        jour_special=jour_special_partiel_beaute_divine,
        heure_debut=time(10, 0),
        heure_fin=time(16, 0)
    )
    print(f"    -> Plage horaire spéciale 10:00-16:00 ajoutée pour le {jour_nouvel_an}.")

salons_existants = list(Salon.objects.all())  # Récupère tous les salons créés
print(f"{len(salons_existants)} salons de test prêts.")

# --- Création des types de Soins (Soin) et de leurs détails par Salon (SoinSalonDetail) ---
print("\nCréation des types de soins et de leurs détails par salon...")

for soin_data in types_de_soins_base:
    # CRÉATION DU SOIN GÉNÉRAL SANS LA DURÉE
    soin_general = Soin.objects.create(
        type_de_soin=soin_data['nom'],
        # LA DUREE N'EST PLUS ICI POUR LE MODELE SOIN
    )
    print(f"Type de Soin général '{soin_general.type_de_soin}' créé.")

    for salon in salons_existants:
        # Générer un prix et un commentaire aléatoires pour chaque Soin-Salon
        prix_specifique = round(random.uniform(soin_data['duree_min'] * 0.8, soin_data['duree_min'] * 1.5), 2)
        commentaire_specifique = (f"Soin spécifique pour le '{soin_general.type_de_soin.lower()}' chez '{salon.nom}'. "
                                  f"Prix variable selon le salon.")

        # CRÉATION DU SOIN_SALON_DETAIL AVEC LA DURÉE
        SoinSalonDetail.objects.create(
            soin=soin_general,
            salon=salon,
            prix=prix_specifique,
            commentaire_specifique=commentaire_specifique,
            duree=timedelta(minutes=soin_data['duree_min']),  # AJOUT DE LA DUREE ICI
        )
        print(
            f"  -> Détail pour '{soin_general.type_de_soin}' chez '{salon.nom}' (Prix: {prix_specifique}€, Durée: "
            f"{timedelta(minutes=soin_data['duree_min'])}) créé.")

print("\n✅ Base de test générée avec succès.")
print("ℹ️ Identifiants test : email = jonjonlacourt@live.be / lacourt (professionnel), user0@exemple.com "
      "(jusqu'à user9) / mdp")
