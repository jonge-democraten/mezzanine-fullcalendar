from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.http import JsonResponse, Http404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.views.generic import TemplateView, DetailView
from django.views.generic.list import MultipleObjectTemplateResponseMixin, ListView
from django.views.generic.dates import BaseDateListView, YearMixin, MonthMixin
from mezzanine.utils.sites import current_site_id

from fullcalendar.models import Event, Occurrence

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
            start_time = timezone.make_aware(occurrence.start_time,
                timezone.get_default_timezone())

            start_json = start_time.strftime('%Y-%m-%dT%H:%M:%S%z')
            start_json = start_json[:-2] + ":" + start_json[-2:]

            end_time = timezone.make_aware(occurrence.end_time,
                timezone.get_default_timezone())

            end_json = end_time.strftime('%Y-%m-%dT%H:%M:%S%z')
            end_json = end_json[:-2] + ":" + end_json[-2:]

            events.append({
                'id': str(occurrence.event.id),
                'title': occurrence.title,
                'start': start_json,
                'end': end_json,
                'url': occurrence.get_absolute_url(),
            })

        return events


class CalendarView(YearMixin, MonthMixin, TemplateView):
    template_name = "events/calendar.html"

    def get_month(self):
        try:
            month = super(CalendarView, self).get_month()
        except Http404:
            month = datetime.now().month

        return month

    def get_year(self):
        try:
            year = super(CalendarView, self).get_year()
        except Http404:
            year = datetime.now().year

        return year

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)

        current = datetime.now()
        month = int(self.get_month())
        year = int(self.get_year())

        if current.month == month and current.year == year:
            day = current.day
        else:
            day = 1

        dt = datetime(year=year, month=month, day=day)

        context.update({
            'json_uri': self.request.build_absolute_uri(
                reverse('fullcalendar-calendar-json')),
            'default_date': dt.strftime('%Y-%m-%d')
        })

        return context


class AgendaView(ListView):
    context_object_name = "occurrence_list"
    paginate_by = 20

    def get_queryset(self):
        if current_site_id() == settings.SITE_ID:
            return Occurrence.objects.upcoming()
        else:
            return Occurrence.site_related.upcoming()

class EventView(DetailView):
    queryset = Event.objects.all()
    context_object_name = 'event'

