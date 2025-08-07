# gestion/views/__init__.py

# Importe toutes les fonctions nécessaires de main_views
from .main_views import home, login_view, logout_view, apropos

# Importe toutes les fonctions nécessaires de utilisateur_views
from .utilisateur_views import utilisateur_list, utilisateur_create, utilisateur_update, utilisateur_delete

# Importe toutes les fonctions nécessaires de soin_views (NOMS DE FONCTIONS CORRIGÉS)
from .soin_views import (
    soin_list,  # Anciennement 'soins'
    soin_create_general,
    soin_update_general,  # Anciennement 'soin_update'
    soin_delete_general,  # Anciennement 'soin_delete'
    soin_salon_detail_create,
    soin_salon_detail_update,
)

# Importe toutes les fonctions nécessaires de salon_views
from .salon_views import (
    liste_salons, detail_salon, ajouter_salon, modifier_salon, supprimer_salon,

)

# Importe toutes les fonctions nécessaires de rendezvous (si elles sont spécifiques à ce fichier et non dans
# salon_views) Attention: si ajouter_rendezvous, modifier_rendezvous, supprimer_rendezvous existent DANS
# rendezvous.py ET salon_views.py, tu auras un conflit ou une confusion. Idéalement, chaque fonction doit être
# unique. Si tes fonctions génériques de RDV sont dans rendezvous.py, alors:
from .rendezvous import (
    rendezvous_view,
    # Si ces fonctions sont aussi ici, décommente:
    # ajouter_rendezvous,
    # modifier_rendezvous,
    # supprimer_rendezvous,
)
