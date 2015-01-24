import calendar
import itertools
from datetime import datetime, timedelta

from django import http
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import JsonResponse, Http404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import MultipleObjectTemplateResponseMixin, ListView
from django.views.generic.dates import BaseDateListView
from mezzanine.utils.sites import current_site_id

from swingtime.models import Event, Occurrence
from swingtime import utils, forms
from swingtime.conf import settings as swingtime_settings

from dateutil import parser

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)

class JSONResponseMixin:
    """
        A mixin class to render a view as JSON
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
            Returns a JSON response based on the context
        """

        return JsonResponse(
            self.get_data(context),
            safe=False,
            **response_kwargs
        )

    def get_data(self, context):
        return context


class DateRangeMixin:
    """
        A mixin class for a view quering objects inside a date range

        :Attributes:

        * ``start`` The start date, defaults to the current date
        * ``start_format`` The format of the start date. Defaults to
          %Y-%m-%d
        * ``end`` (Optional). The end date
        * ``end_format`` The format of the end date. Defaults to
          %Y-%m-%d
    """

    start = None
    start_format = "%Y-%m-%d"

    end = None
    end_format = "%Y-%m-%d"

    def get_start(self):
        start = self.start

        if start is None:
            try:
                start = self.kwargs['start']
            except KeyError:
                try:
                    start = self.request.GET['start']
                except KeyError:
                    raise Http404(_("No start date specified"))

        return start

    def get_start_format(self):
        return self.start_format

    def get_end(self):
        end = self.end

        if end is None:
            try:
                end = self.kwargs['end']
            except KeyError:
                try:
                    end = self.request.GET['end']
                except KeyError:
                    raise Http404(_("No end date specified"))

        return end

    def get_end_format(self):
        return self.end_format


class DateMixin2:
    """
        A class which is actually almost the same as the default django date mixin
        class, but with different field names, so you can have two date fields.

        This is useful if you have objects with for example a start and end date.
    """

    date_field2 = None

    def get_date_field2(self):
        if self.date_field2 is None:
            raise ImproperlyConfigured(_("{}.date_field is required").format(
                self.__class__.name))

        return self.date_field2

    @cached_property
    def field2_uses_datetime(self):
        model = self.get_queryset().model if self.model is None else self.model
        field = model._meta.get_field(self.get_date_field2())

        return isinstance(field, models.DateTimeField)

    def _make_date_lookup_arg2(self, value):
        """
            Convert a date into a datetime when the date field is a DateTimeField.

            When time zone support is enabled, `date` is assumed to be in the
            current time zone, so that displayed items are consistent with the URL.
        """
        if self.field2_uses_datetime:
            value = datetime.datetime.combine(value, datetime.time.min)
            if settings.USE_TZ:
                value = timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def _make_single_date_lookup2(self, date):
        """
            Get the lookup kwargs for filtering on a single date.

            If the date field is a DateTimeField, we can't just filter on
            date_field=date because that doesn't take the time into account.
        """

        date_field = self.get_date_field2()
        if self.field2_uses_datetime:
            since = self._make_date_lookup_arg(date)
            until = self._make_date_lookup_arg(date + datetime.timedelta(days=1))
            return {
                '%s__gte' % date_field: since,
                '%s__lt' % date_field: until,
            }
        else:
            # Skip self._make_date_lookup_arg, it's a no-op in this branch.
            return {date_field: date}


class BaseDateRangeView(DateRangeMixin, DateMixin2, BaseDateListView):
    """
        A view to display objects in a given date range

        Through ``BaseDateListView``, this class inhirits from ``DateMixin``. The
        date field specified for this class is used for the start date.

        We also inhirit from ``DateMixin2``, which adds date_field2. The field
        specified in this attribute is used for the end date.
    """

    allow_future = True
    allow_empty = True

    def get_dated_items(self):
        """
            Return (date_list, items, extra_context) for this request in a certain
            date range
        """

        start = self.get_start()
        end = self.get_end()

        try:
            date_start = datetime.strptime(start, self.get_start_format())
        except ValueError:
            raise Http404(_("Invalid date string '{datestr}' given format"
                " '{format}'").format(datestr=start, format=self.get_start_format()))

        try:
            date_end = datetime.strptime(end, self.get_end_format())
        except ValueError:
            raise Http404(_("Invalid date string '{datestr}' given format"
                " '{format}'").format(datestr=end, format=self.get_end_format()))

        date_field = self.get_date_field()
        date_field2 = self.get_date_field2()

        # Select all objects which at least have some overlapping with the
        # given range. This means the end date of an object should be greater
        # than the given start date, and the start date of an object should be
        # smaller than the given end date.
        date_filter = {
            '%s__gte' % date_field2: date_start,
            '%s__lte' % date_field: date_end
        }

        qs = self.get_dated_queryset(date_field, **date_filter)
        date_list = self.get_date_list(qs)

        return (date_list, qs, {})


class BaseCalendarView(MultipleObjectTemplateResponseMixin, BaseDateRangeView):
    template_name_suffix = "_calendar"


class CalendarJSONView(JSONResponseMixin, BaseCalendarView):
    model = Occurrence
    date_field = "start_time"
    date_field2 = "end_time"

    def get_queryset(self):
        print(current_site_id())
        if current_site_id() == settings.SITE_ID:
            return self.model.objects.select_related('event')
        else:
            return self.model.site_related.select_related('event')

    def render_to_response(self, context, **kwargs):
        context = self.get_context_data()

        # return render(self.request, "test.html", context)
        return self.render_to_json_response(context, **kwargs)

    def get_data(self, context):
        events = []

        for occurrence in context['object_list']:
            title = occurrence.event.title

            if occurrence.description:
                title = "{} - {}".format(occurrence.description, title)

            events.append({
                'id': occurrence.event.id,
                'title': title,
                'start': occurrence.start_time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'end': occurrence.end_time.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'url': occurrence.get_absolute_url(),
            })

        return events


class CalendarView(BaseCalendarView):
    template_suffix = "calendar_all"

    def get_queryset(self):
        if current_site_id() == settings.SITE_ID:
            return self.model.objects.select_related('event')
        else:
            return self.model.site_related.select_related('event')


class AgendaView(ListView):
    model = Occurrence

    def get_queryset(self):
        if current_site_id() == settings.SITE_ID:
            return Occurrence.objects.upcoming()
        else:
            return Occurrence.site_related.upcoming()


def event_listing(
    request,
    template='swingtime/event_list.html',
    events=None,
    **extra_context
):
    '''
    View all ``events``.

    If ``events`` is a queryset, clone it. If ``None`` default to all ``Event``s.

    Context parameters:

    events
        an iterable of ``Event`` objects

    ???
        all values passed in via **extra_context
    '''
    return render(
        request,
        template,
        dict(extra_context, events=events or Event.objects.all())
    )

def event_view(
    request,
    pk,
    template='swingtime/event_detail.html',
    event_form_class=forms.EventForm,
    recurrence_form_class=forms.MultipleOccurrenceForm
):
    '''
    View an ``Event`` instance and optionally update either the event or its
    occurrences.

    Context parameters:

    event
        the event keyed by ``pk``

    event_form
        a form object for updating the event

    recurrence_form
        a form object for adding occurrences
    '''
    event = get_object_or_404(Event, pk=pk)
    event_form = recurrence_form = None
    if request.method == 'POST':
        if '_update' in request.POST:
            event_form = event_form_class(request.POST, instance=event)
            if event_form.is_valid():
                event_form.save(event)
                return http.HttpResponseRedirect(request.path)
        elif '_add' in request.POST:
            recurrence_form = recurrence_form_class(request.POST)
            if recurrence_form.is_valid():
                recurrence_form.save(event)
                return http.HttpResponseRedirect(request.path)
        else:
            return http.HttpResponseBadRequest('Bad Request')

    data = {
        'event': event,
        'event_form': event_form or event_form_class(instance=event),
        'recurrence_form': recurrence_form or recurrence_form_class(
            initial={'dtstart': datetime.now()})
    }
    return render(request, template, data)

def occurrence_view(
    request,
    event_pk,
    pk,
    template='swingtime/occurrence_detail.html',
    form_class=forms.SingleOccurrenceForm
):
    '''
    View a specific occurrence and optionally handle any updates.

    Context parameters:

    occurrence
        the occurrence object keyed by ``pk``

    form
        a form object for updating the occurrence
    '''
    occurrence = get_object_or_404(Occurrence, pk=pk, event__pk=event_pk)
    if request.method == 'POST':
        form = form_class(request.POST, instance=occurrence)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(request.path)
    else:
        form = form_class(instance=occurrence)

    return render(request, template, {'occurrence': occurrence, 'form': form})

def add_event(
    request,
    template='swingtime/add_event.html',
    event_form_class=forms.EventForm,
    recurrence_form_class=forms.MultipleOccurrenceForm
):
    '''
    Add a new ``Event`` instance and 1 or more associated ``Occurrence``s.

    Context parameters:

    dtstart
        a datetime.datetime object representing the GET request value if present,
        otherwise None

    event_form
        a form object for updating the event

    recurrence_form
        a form object for adding occurrences

    '''
    dtstart = None
    if request.method == 'POST':
        event_form = event_form_class(request.POST)
        recurrence_form = recurrence_form_class(request.POST)
        if event_form.is_valid() and recurrence_form.is_valid():
            event = event_form.save()
            recurrence_form.save(event)
            return http.HttpResponseRedirect(event.get_absolute_url())

    else:
        if 'dtstart' in request.GET:
            try:
                dtstart = parser.parse(request.GET['dtstart'])
            except:
                # TODO A badly formatted date is passed to add_event
                pass

        dtstart = dtstart or datetime.now()
        event_form = event_form_class()
        recurrence_form = recurrence_form_class(initial={'dtstart': dtstart})

    return render(
        request,
        template,
        {
            'dtstart': dtstart,
            'event_form': event_form,
            'recurrence_form': recurrence_form
        }
    )

def _datetime_view(
    request,
    template,
    dt,
    timeslot_factory=None,
    items=None,
    params=None
):
    '''
    Build a time slot grid representation for the given datetime ``dt``. See
    utils.create_timeslot_table documentation for items and params.

    Context parameters:

    day
        the specified datetime value (dt)

    next_day
        day + 1 day

    prev_day
        day - 1 day

    timeslots
        time slot grid of (time, cells) rows

    '''
    timeslot_factory = timeslot_factory or utils.create_timeslot_table
    params = params or {}

    return render(request, template, {
        'day':       dt,
        'next_day':  dt + timedelta(days=+1),
        'prev_day':  dt + timedelta(days=-1),
        'timeslots': timeslot_factory(dt, items, **params)
    })

def day_view(request, year, month, day,
        template='swingtime/daily_view.html', **params):
    '''
    See documentation for function``_datetime_view``.

    '''
    dt = datetime(int(year), int(month), int(day))
    return _datetime_view(request, template, dt, **params)

def today_view(request, template='swingtime/daily_view.html', **params):
    '''
    See documentation for function``_datetime_view``.

    '''
    return _datetime_view(request, template, datetime.now(), **params)

def year_view(request, year, template='swingtime/yearly_view.html', queryset=None):
    '''

    Context parameters:

    year
        an integer value for the year in questin

    next_year
        year + 1

    last_year
        year - 1

    by_month
        a sorted list of (month, occurrences) tuples where month is a
        datetime.datetime object for the first day of a month and occurrences
        is a (potentially empty) list of values for that month. Only months
        which have at least 1 occurrence is represented in the list

    '''
    year = int(year)
    queryset = queryset._clone() if queryset else Occurrence.objects.select_related()
    occurrences = queryset.filter(
        models.Q(start_time__year=year) |
        models.Q(end_time__year=year)
    )

    def group_key(o):
        return datetime(
            year,
            o.start_time.month if o.start_time.year == year else o.end_time.month,
            1
        )

    return render(request, template, {
        'year': year,
        'by_month': [
            (dt, list(o)) for dt, o in itertools.groupby(occurrences, group_key)
        ],
        'next_year': year + 1,
        'last_year': year - 1

    })

def month_view(
    request,
    year,
    month,
    template='swingtime/monthly_view.html',
    queryset=None
):
    '''
    Render a tradional calendar grid view with temporal navigation variables.

    Context parameters:

    today
        the current datetime.datetime value

    calendar
        a list of rows containing (day, items) cells, where day is the day of
        the month integer and items is a (potentially empty) list of occurrence
        for the day

    this_month
        a datetime.datetime representing the first day of the month

    next_month
        this_month + 1 month

    last_month
        this_month - 1 month

    '''
    year, month = int(year), int(month)
    cal = calendar.monthcalendar(year, month)
    dtstart = datetime(year, month, 1)
    last_day = max(cal[-1])

    # TODO Whether to include those occurrences that started in the previous
    # month but end in this month?
    queryset = queryset._clone() if queryset else Occurrence.objects.select_related()
    occurrences = queryset.filter(start_time__year=year, start_time__month=month)

    def start_day(o):
        return o.start_time.day

    by_day = dict(
        [(dt, list(o)) for dt, o in itertools.groupby(occurrences, start_day)]
    )

    data = {
        'today':      datetime.now(),
        'calendar':   [[(d, by_day.get(d, [])) for d in row] for row in cal],
        'this_month': dtstart,
        'next_month': dtstart + timedelta(days=+last_day),
        'last_month': dtstart + timedelta(days=-1),
    }

    return render(request, template, data)

