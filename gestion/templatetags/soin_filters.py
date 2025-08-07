# gestion/templatetags/soin_filters.py

from django import template

register = template.Library()


@register.filter
def total_minutes(duration):
    """
    Retourne la durée totale en minutes à partir d'un objet timedelta.
    """
    if duration:
        return int(duration.total_seconds() / 60)
    return 0


@register.filter
def format_duration(duration):
    """
    Formate un objet timedelta en "Xh Ym" ou "Ym".
    """
    if not duration:
        return "N/A"
    total_minutes = int(duration.total_seconds() / 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "0m"  # Si la durée est zéro
