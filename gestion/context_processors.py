def utilisateur_context(request):
    return {
        'utilisateur_id': request.session.get('utilisateur_id'),
        'utilisateur_nom': request.session.get('utilisateur_nom'),
        'utilisateur_prenom': request.session.get('utilisateur_prenom'),
        'utilisateur_role': request.session.get('utilisateur_role'),
    }
