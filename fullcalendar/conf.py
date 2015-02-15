from datetime import timedelta

from django.conf import settings as django_settings

default = {
    'FULLCALENDAR_FIRST_WEEKDAY': 0,
    'FULLCALENDAR_OCCURRENCE_DURATION': timedelta(hours=1),
    'FULLCALENDAR_SITE_COLORS': {}
}

settings = object()

for key, value in default.items():
    setattr(settings, key,
        getattr(django_settings, key, value))
