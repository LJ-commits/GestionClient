# GestionClient/gestion/urls.py

from django.urls import path

from gestion.views import horaires_views, main_views, \
    rendezvous  # Importe explicitement les modules utilisés pour la clarté
from gestion.views import salon_views  # Importe salon_views pour ses routes spécifiques
from gestion.views import soin_views  # Importe soin_views
from gestion.views import utilisateur_views  # Importe utilisateur_views

urlpatterns = [
    # Vues générales (main_views.py)
    path('accueil/', main_views.home, name='home'),
    path('login/', main_views.login_view, name='login'),
    path('logout/', main_views.logout_view, name='logout'),
    path('creer-compte/', main_views.register_view, name='register'),
    path('apropos/', main_views.apropos, name='apropos'),

    # Routes utilisateurs (utilisateur_views.py)
    path('utilisateurs/', utilisateur_views.utilisateur_list, name='utilisateur_list'),
    path('utilisateurs/create/', utilisateur_views.utilisateur_create, name='utilisateur_create'),
    path('utilisateurs/<int:pk>/update/', utilisateur_views.utilisateur_update, name='utilisateur_update'),
    path('utilisateurs/<int:pk>/delete/', utilisateur_views.utilisateur_delete, name='utilisateur_delete'),
    path('utilisateurs/toggle-active/<int:pk>/', utilisateur_views.utilisateur_toggle_active,
         name='utilisateur_toggle_active'),
    path('utilisateurs/<int:pk>/password/', utilisateur_views.utilisateur_set_password,
         name='utilisateur_set_password'),

    # Routes soins (soin_views.py)
    path('soins/', soin_views.soin_list, name='soins'),
    path('soins/create-general/', soin_views.soin_create_general, name='soin_create_general'),
    path('soins/<int:pk>/update-general/', soin_views.soin_update_general, name='soin_update_general'),
    path('soins/<int:pk>/delete-general/', soin_views.soin_delete_general, name='soin_delete_general'),
    path('salons/<int:salon_pk>/soins-details/', soin_views.soin_salon_detail_list,
         name='soin_salon_detail_list'),
    path('salons/<int:salon_pk>/soins-details/create/', soin_views.soin_salon_detail_create,
         name='soin_salon_detail_create'),
    path('soins/details/<int:pk>/update/', soin_views.soin_salon_detail_update, name='soin_salon_detail_update'),
    path('soins/details/<int:pk>/delete/', soin_views.soin_salon_detail_delete, name='soin_salon_detail_delete'),

    # Routes salons (salon_views.py)
    path('salons/', salon_views.liste_salons, name='liste_salons'),
    path('salons/<int:pk>/', salon_views.detail_salon, name='detail_salon'),
    path('salons/<int:pk>/rendezvous-anciens/', salon_views.anciens_rendezvous, name='anciens_rendezvous'),
    path('salons/<int:pk>/modifier/', salon_views.modifier_salon, name='modifier_salon'),
    path('salons/<int:pk>/supprimer/', salon_views.supprimer_salon, name='supprimer_salon'),
    path('salons/ajouter/', salon_views.ajouter_salon, name='ajouter_salon'),

    # Routes pour la gestion des plages horaires régulières (horaires_views.py)
    path('salons/<int:pk>/plages/', horaires_views.liste_plages_horaires, name='liste_plages_horaires'),
    path('salons/<int:pk>/plages/ajouter/', horaires_views.ajouter_plage_horaire, name='ajouter_plage_horaire'),
    path('salons/<int:salon_pk>/plages/<int:plage_pk>/modifier/', horaires_views.modifier_plage_horaire,
         name='modifier_plage_horaire'),
    path('salons/<int:salon_pk>/plages/<int:plage_pk>/supprimer/', horaires_views.supprimer_plage_horaire,
         name='supprimer_plage_horaire'),

    # Routes pour la gestion des Jours Spéciaux (horaires_views.py)
    path('salons/<int:pk>/jours-speciaux/', horaires_views.liste_jours_speciaux, name='liste_jours_speciaux'),
    path('salons/<int:pk>/jours-speciaux/ajouter/', horaires_views.ajouter_jour_special, name='ajouter_jour_special'),
    path('salons/<int:pk>/jours-speciaux/ajouter-periode-vacances/', horaires_views.ajouter_periode_vacances,
         name='ajouter_periode_vacances'),
    path('salons/<int:salon_pk>/jours-speciaux/<int:jour_special_pk>/modifier/', horaires_views.modifier_jour_special,
         name='modifier_jour_special'),
    path('salons/<int:salon_pk>/jours-speciaux/<int:jour_special_pk>/supprimer/', horaires_views.supprimer_jour_special,
         name='supprimer_jour_special'),
    # --- DÉBUT MODIFICATION ---
    # La nouvelle route pour la suppression d'une période de vacances
    path('salons/<int:salon_pk>/jours-speciaux/supprimer-period/', horaires_views.supprimer_periode_vacances,
         name='supprimer_periode_vacances'),
    # --- FIN MODIFICATION ---

    # Routes pour la gestion des Plages Horaires Spéciales (horaires_views.py)
    path('salons/<int:salon_pk>/jours-speciaux/<int:jour_special_pk>/plages-speciales/',
         horaires_views.liste_plages_horaires_speciales, name='liste_plages_horaires_speciales'),
    path('salons/<int:salon_pk>/jours-speciaux/<int:jour_special_pk>/plages-speciales/ajouter/',
         horaires_views.ajouter_plage_horaire_speciale, name='ajouter_plage_horaire_speciale'),
    path('salons/<int:salon_pk>/jours-speciaux/<int:jour_special_pk>/plages-speciales/'
         '<int:plage_speciale_pk>/modifier/', horaires_views.modifier_plage_horaire_speciale,
         name='modifier_plage_horaire_speciale'),
    path('salons/<int:salon_pk>/jours-speciaux/'
         '<int:jour_special_pk>/plages-speciales/<int:plage_speciale_pk>/supprimer/',
         horaires_views.supprimer_plage_horaire_speciale, name='supprimer_plage_horaire_speciale'),

    # --- ROUTES RENDEZ-VOUS ---
    path('rendezvous/tous/', rendezvous.rendezvous_tous_view, name='rendezvous_tous'),
    path('rendezvous/mes/', rendezvous.mes_rendezvous_view, name='mes_rendezvous'),
    path('salon/<int:salon_id>/rendezvous/ajouter/', rendezvous.ajouter_rendezvous, name='ajouter_rendezvous'),
    path('rendezvous/<int:rendezvous_id>/modifier/', rendezvous.modifier_rendezvous, name='modifier_rendezvous'),
    path('rendezvous/<int:rendezvous_id>/supprimer/', rendezvous.supprimer_rendezvous, name='supprimer_rendezvous'),
    path('rendezvous/<int:pk>/modifier-statut/', rendezvous.modifier_statut_rendezvous,
         name='modifier_statut_rendezvous'),

    # --- NOUVELLES ROUTES RENDEZ-VOUS PERSONNEL ---
    path('rendezvous/prendre/choisir-salon/', rendezvous.choisir_salon_pour_rendezvous,
         name='choisir_salon_pour_rendezvous'),
    path('rendezvous/prendre/salon/<int:salon_id>/', rendezvous.prendre_rendezvous_personnel,
         name='prendre_rendezvous_personnel'),
]
