Calendar application for Mezzanine using the fullcalendar.io widget
===================================================================

Mezzanine-fullcalendar is a calendar application for
`Mezzanine <http://mezzanine.jupo.org/>`_, using the awesome
`fullcalendar.io <http://fullcalendar.io>`_ javascript widget, which provides
a modern looking calendar.

This project originally started out as a fork of `django-swingtime
<https://github.com/dakrauth/django-swingtime>`_, but deviated so much from the
original project, it is now a separate project.

Current features
----------------

* Admin interface for managing events and their occurrences.
* Event categories
* Class based views for the calendar, JSON data, and an agenda view 
  with upcoming events.
* Support for multiple sites

Planned features
----------------

* Make use of the editing features of the fullcalendar javascript widget.
* Create forms for easily adding new events through the calendar.
* ICal export
* More tests and docs

Requirements
------------

* Python 2.7+, 3.4+
* Django 1.6+
* python-dateutil

