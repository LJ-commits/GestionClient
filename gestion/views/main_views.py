# gestion/views/main_views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import cache_control

from gestion.models import Utilisateur
from gestion.forms.utilisateur_forms import UtilisateurCreationForm, UtilisateurPublicRegistrationForm


def home(request):
    context = {
        'nom_entreprise': "Saint Jolie",
        'description': "Nous proposons des soins de qualité pour nos clients.",
        'photo': "img/entreprise.jpg",
    }
    return render(request, 'gestion/home.html', context)


def login_view(request):
    context = {
        'nom_entreprise': 'Saint Jolie',
        'email_saisi': '',
    }

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('mot_de_passe')  # Assure-toi que le 'name' dans login.html est 'mot_de_passe'

        context['email_saisi'] = email

        # Correctement authentifier l'utilisateur
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie. Bienvenue chez Saint Jolie ! ✨")
            return redirect('home')
        else:
            messages.error(request, "Adresse e-mail ou mot de passe incorrect.")

    return render(request, 'gestion/login.html', context)


"""
Ce décorateur envoie des en-têtes HTTP spécifiques au navigateur, lui demandant de :
no_cache : Ne pas enregistrer cette page dans son cache.
no_store : Ne pas la stocker dans l'historique de session ou sur le disque.
must_revalidate : Vérifier auprès du serveur à chaque fois qu'il tente de la charger.

"""


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté. À bientôt ! 👋")
    return redirect('home')


def apropos(request):
    context = {
        'nom_entreprise': "Saint Jolie",
        'description': "Nous sommes spécialisés dans les soins esthétiques de qualité. <br> "
                       " Notre mission est de prendre soin de vous. <br>"
                       " Deux espaces de soins <br>"
                       " Notre institut comporte deux départements: <br>"
                       "Le Quartier Bien-être axés sur l'hydrothérapie (balnéothérapie, watermass et douche "
                       "sous-affusion) <br>"
                       "Le Salon proposant les soins esthétiques classique liés à la beauté du corps, du visage, "
                       "des ongles et du regard. <br>"
                       "Catégories : École d’esthétique <br>"
                       "Coordonnées <br>"
                       "Adresse: Rue Mazy 20, Jambes, Belgium, 5100 <br>"
                       "Mobile: 0493 52 52 84 ",
        'photo': "img/entreprise.jpg",
    }
    return render(request, 'gestion/apropos.html', context)


# Vue d'inscription des utilisateurs
def register_view(request):
    if request.method == 'POST':
        form = UtilisateurPublicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # L'utilisateur est créé mais pas encore connecté

            # --- DÉBUT MODIFICATION ---
            login(request, user)  # Connecte l'utilisateur juste après la création du compte
            messages.success(request, f"Bienvenue {user.first_name} ! Votre compte a été créé et vous êtes connecté. ✨")
            return redirect('home')  # Redirige vers la page d'accueil
            # --- FIN MODIFICATION ---

        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = UtilisateurPublicRegistrationForm()

    context = {
        'form': form,
        'nom_entreprise': 'Saint Jolie',
        'title': 'Créer un compte',
    }
    return render(request, 'gestion/register.html', context)
