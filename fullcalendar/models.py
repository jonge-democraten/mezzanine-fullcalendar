from datetime import datetime

from dateutil import rrule
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.db import models
from mezzanine.core.models import Displayable, RichText, SiteRelated
from mezzanine.core.managers import SearchableManager
from mezzanine.core.managers import PublishedManager
from mezzanine.core.managers import CurrentSiteManager


__all__ = (
    'EventCategory',
    'Event',
    'Occurrence',
    'create_event'
)


@python_2_unicode_compatible
class EventCategory(SiteRelated):
    '''
    Simple ``Event`` classifcation.

    '''
    name = models.CharField(_('name'), max_length=50)
    description = models.CharField(_('description'), blank=True, null=True,
                                   max_length=255)
    color = models.CharField(_('color'), max_length=10, blank=True, null=True)

    class Meta:
        verbose_name = _('event category')
        verbose_name_plural = _('event categories')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Event(Displayable, RichText):
    '''
    Container model for general metadata and associated ``Occurrence`` entries.
    '''
    event_category = models.ForeignKey(
        EventCategory,
        verbose_name=_('event category'), blank=True, null=True
    )

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('title',)

    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        my_occurrences = Occurrence.objects.filter(event__id=self.id)
        for occurrence in my_occurrences:
            occurrence.save()

    @models.permalink
    def get_absolute_url(self):
        occurrences = Occurrence.objects.filter(event__id=self.id)
        if occurrences: # Return first occurrence of the event if it exists...
            return ('fullcalendar-occurrence', [self.slug, str(occurrences[0].id)])
        else: # Otherwise, return the calendar
            return ('fullcalendar-calendar', [])

    def add_occurrences(self, start_time, end_time, **rrule_params):
        '''
        Add one or more occurences to the event using a comparable API to
        ``dateutil.rrule``.

        If ``rrule_params`` does not contain a ``freq``, one will be defaulted
        to ``rrule.DAILY``.

        Because ``rrule.rrule`` returns an iterator that can essentially be
        unbounded, we need to slightly alter the expected behavior here in order
        to enforce a finite number of occurrence creation.

        If both ``count`` and ``until`` entries are missing from ``rrule_params``,
        only a single ``Occurrence`` instance will be created using the exact
        ``start_time`` and ``end_time`` values.
        '''
        rrule_params.setdefault('freq', rrule.DAILY)

        if 'count' not in rrule_params and 'until' not in rrule_params:
            self.occurrence_set.create(start_time=start_time, end_time=end_time)
        else:
            delta = end_time - start_time
            for ev in rrule.rrule(dtstart=start_time, **rrule_params):
                self.occurrence_set.create(start_time=ev, end_time=ev + delta)

    def upcoming_occurrences(self):
        '''
        Return all occurrences that are set to start on or after the current
        time.
        '''
        return self.occurrence_set.published().filter(
            start_time__gte=datetime.now())

    def next_occurrence(self):
        '''
        Return the single occurrence set to start on or after the current time
        if available, otherwise ``None``.
        '''
        upcoming = self.upcoming_occurrences()
        return upcoming and upcoming[0] or None

    def daily_occurrences(self, dt=None):
        '''
        Convenience method wrapping ``Occurrence.objects.daily_occurrences``.
        '''
        return Occurrence.objects.daily_occurrences(dt=dt, event=self)


class OccurrenceManager(PublishedManager, SearchableManager):

    use_for_related_fields = True

    def get_queryset(self):
        """
        Occurrence objects will mostly also need information from its
        event object, so join it by default
        """
        qs = super(OccurrenceManager, self).get_queryset()

        return qs.select_related('event')

    def upcoming(self, start=None, end=None, for_user=None):
        """
        Returns a queryset containing the upcoming occurences no matter what
        event.

        * ``start`` A datetime object with the minimum date and time an occurence
          should have. Defaults to ``timezone.now()``.
        * ``end`` (Optional). Only retrieve occurrences no later than the given
          datetime object.
        """

        start = start or timezone.now()

        qs = self.published(for_user=for_user).filter(start_time__gte=start)

        if end:
            qs.filter(start_time__lte=end)

        return qs

    def daily_occurrences(self, dt=None, event=None):
        '''
        Returns a queryset of for instances that have any overlap with a
        particular day.

        * ``dt`` may be either a datetime.datetime, datetime.date object, or
          ``None``. If ``None``, default to the current day.

        * ``event`` can be an ``Event`` instance for further filtering.
        '''
        dt = dt or datetime.now()
        start = datetime(dt.year, dt.month, dt.day)
        end = start.replace(hour=23, minute=59, second=59)
        qs = self.published().filter(
            models.Q(
                start_time__gte=start,
                start_time__lte=end,
            ) |
            models.Q(
                end_time__gte=start,
                end_time__lte=end,
            ) |
            models.Q(
                start_time__lt=start,
                end_time__gt=end
            )
        )

        return qs.filter(event=event) if event else qs


class SiteRelatedOccurrenceManager(CurrentSiteManager, OccurrenceManager):
    def get_queryset(self):
        # the intersection of the query sets of both managers
        return CurrentSiteManager.get_queryset(self) & OccurrenceManager.get_queryset(self)


@python_2_unicode_compatible
class Occurrence(Displayable):
    '''
    Represents the start end time for a specific occurrence of a master ``Event``
    object.
    '''
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    event = models.ForeignKey(Event, verbose_name=_('event'), editable=False)
    location = models.CharField(_('location'), max_length=255, blank=True, null=True)

    objects = OccurrenceManager()
    site_related = SiteRelatedOccurrenceManager()

    class Meta:
        verbose_name = _('occurrence')
        verbose_name_plural = _('occurrences')
        ordering = ('start_time', 'end_time')

    def __str__(self):
        return '%s: %s' % (self.title, self.start_time.strftime('%Y-%m-%d - %H:%M'))

    @models.permalink
    def get_absolute_url(self):
        return ('fullcalendar-occurrence', [self.event.slug, str(self.id)])

    def __lt__(self, other):
        return self.start_time < other.start_time

    @property
    def event_category(self):
        return self.event.event_category

    @property
    def in_past(self):
        return self.end_time < timezone.now()

    def save(self, *args, **kwargs):
        self.gen_description = False
        if self.description:
            self.title = self.event.title + ' (' + self.description + ')'
        else:
            self.title = self.event.title
        self.status = self.event.status
        self.publish_date = self.event.publish_date
        self.expiry_date = self.event.expiry_date
        super(Occurrence, self).save(*args, **kwargs)


def create_event(
    title,
    event_category,
    description='',
    start_time=None,
    end_time=None,
    **rrule_params
):
    '''
    Convenience function to create an ``Event``, optionally create an
    ``EventCategory``, and associated ``Occurrence``s. ``Occurrence`` creation
    rules match those for ``Event.add_occurrences``.

    Returns the newly created ``Event`` instance.

    Parameters

    ``event_category``
        can be either an ``EventCategory`` object or string,
        from which an ``EventCategory`` is either created or retrieved.

    ``start_time``
        will default to the current hour if ``None``

    ``end_time``
        will default to ``start_time`` plus
        fullcalendar_settings.DEFAULT_OCCURRENCE_DURATION hour if ``None``

    ``freq``, ``count``, ``rrule_params``
        follow the ``dateutils`` API (see http://labix.org/python-dateutil)

    '''
    from fullcalendar.conf import settings as fullcalendar_settings

    if isinstance(event_category, str):
        event_category, created = EventCategory.objects.get_or_create(
            name=event_category
        )

    event = Event.objects.create(
        title=title,
        content=description,
        event_category=event_category
    )

    start_time = start_time or datetime.now().replace(
        minute=0,
        second=0,
        microsecond=0
    )

    end_time = end_time or \
        start_time + fullcalendar_settings.FULLCALENDAR_OCCURRENCE_DURATION
    event.add_occurrences(start_time, end_time, **rrule_params)
    return event
