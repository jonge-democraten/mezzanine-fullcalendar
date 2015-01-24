from django.conf.urls import patterns, url
from swingtime import views

urlpatterns = patterns('',
    url(
        r'^(?:calendar/)?$',
        views.CalendarView.as_view(),
        name='swingtime-calendar'
    ),

    url(
        r'^calendar/json/$',
        views.CalendarJSONView.as_view(),
        name='swingtime-calendar-json'
    ),

    url(
        r'^calendar/(?P<year>\d{4})/$',
        views.CalendarView.as_view(),
        name='swingtime-yearly-view'
    ),

    url(
        r'^calendar/(\d{4})/(0?[1-9]|1[012])/$',
        views.CalendarView.as_view(),
        name='swingtime-monthly-view'
    ),

    url(
        r'^agenda/$',
        views.AgendaView.as_view(),
        name='swingtime-events'
    ),

    url(
        r'^event/(\d+)/$',
        views.event_view,
        name='swingtime-event'
    ),

    url(
        r'^event/(\d+)/occurrence/(\d+)/$',
        views.occurrence_view,
        name='swingtime-occurrence'
    ),
)
