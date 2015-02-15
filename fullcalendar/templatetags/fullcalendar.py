from django import template

from fullcalendar.models import Occurrence

register = template.Library()

@register.inclusion_tag('events/agenda_tag.html')
def show_agenda(*args, **kwargs):
    qs = Occurrence.objects.upcoming()

    if 'limit' in kwargs:
        qs.limit(int(kwargs['limit']))

    return {
        'occurrences': qs,
        'all_sites': True,
    }

@register.assignment_tag
def get_agenda(*args, **kwargs):
    qs = Occurrence.site_related.upcoming()

    if 'limit' in kwargs:
        qs.limit(int(kwargs['limit']))

    return qs


@register.inclusion_tag('events/agenda_tag.html')
def show_site_agenda(*args, **kwargs):
    qs = Occurrence.site_related.upcoming()

    if 'limit' in kwargs:
        qs.limit(int(kwargs['limit']))

    return {
        'occurrences': qs
    }

@register.assignment_tag
def get_site_agenda(*args, **kwargs):
    qs = Occurrence.site_related.upcoming()

    if 'limit' in kwargs:
        qs.limit(int(kwargs['limit']))

    return qs

