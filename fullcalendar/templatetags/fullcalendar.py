from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import timezone

from mezzanine import template
from mezzanine.utils.sites import current_site_id

from fullcalendar.models import Occurrence

register = template.Library()


@register.inclusion_tag('events/agenda_tag.html', takes_context=True)
def show_agenda(context, *args, **kwargs):
    qs = Occurrence.objects.upcoming(for_user=context['request'].user)

    if 'limit' in kwargs:
        qs = qs[:int(kwargs['limit'])]

    return {
        'occurrences': qs,
        'all_sites': True,
    }


@register.assignment_tag(takes_context=True)
def get_agenda(context, *args, **kwargs):
    qs = Occurrence.objects.upcoming(for_user=context['request'].user)

    if 'limit' in kwargs:
        return qs[:int(kwargs['limit'])]

    return qs


@register.inclusion_tag('events/agenda_tag.html', takes_context=True)
def show_site_agenda(context, *args, **kwargs):
    qs = Occurrence.site_related.upcoming(for_user=context['request'].user)

    if 'limit' in kwargs:
        qs = qs[:int(kwargs['limit'])]

    return {
        'occurrences': qs
    }


@register.assignment_tag(takes_context=True)
def get_site_agenda(context, *args, **kwargs):
    qs = Occurrence.site_related.upcoming(for_user=context['request'].user)

    if 'limit' in kwargs:
        return qs[:int(kwargs['limit'])]

    return qs


@register.assignment_tag(takes_context=True)
def get_site_and_main_agenda(context, *args, **kwargs):
    qs_main = Occurrence.objects.upcoming(for_user=context['request'].user).filter(
        event__site__id__exact=1)
    qs_site = get_site_agenda(context, *args, **kwargs)
    qs = qs_main | qs_site

    if 'limit' in kwargs:
        return qs[:int(kwargs['limit'])]

    return qs


@register.simple_tag
def occurrence_duration(occurrence):
    start = timezone.localtime(occurrence.start_time)
    end = timezone.localtime(occurrence.end_time)
    result = start.strftime('%A, %d %B %Y %H:%M')

    if (start.day == end.day and start.month == end.month and
            start.year == end.year):
        result += ' - {:%H:%M}'.format(end)
    else:
        result += ' - {:%A, %d %B %Y %H:%M}'.format(end)

    return result


@register.inclusion_tag("events/site_legend.html")
def events_site_legend():
    from fullcalendar.conf import settings as fc_settings

    sites = {}
    for site in Site.objects.all():
        sites[site.id] = site.name

    context = {
        'legend': {}
    }
    if current_site_id() != settings.SITE_ID:
        return context
    for site, color in fc_settings.FULLCALENDAR_SITE_COLORS.items():
        data = {}
        if type(color) == str:
            data['backgroundColor'] = color
            data['textColor'] = 'white'
            data['borderColor'] = color
        else:
            if len(color) == 2:
                data['backgroundColor'] = color[0]
                data['textColor'] = color[1]
                data['borderColor'] = color[0]
            elif len(color) > 2:
                data['backgroundColor'] = color[0]
                data['textColor'] = color[1]
                data['borderColor'] = color[2]

        site_name = sites[site]
        context['legend'][site_name] = data

    return context
