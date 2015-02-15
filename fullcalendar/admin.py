from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from mezzanine.core.admin import TabularDynamicInlineAdmin, DisplayableAdmin

from fullcalendar.models import *

class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class OccurrenceInline(TabularDynamicInlineAdmin):
    model = Occurrence
    extra = 1

class EventAdmin(DisplayableAdmin):
    list_display = ('title', 'event_category')
    list_filter = ('event_category',)
    search_fields = ('title', 'description', 'content', 'keywords')

    fieldsets = (
        (None, {
            "fields": [
                "title", "status", ("publish_date", "expiry_date"),
                "event_category", "content"
            ]
        }),
        (_("Meta data"), {
            "fields": [
                "_meta_title", "slug",
                ("description", "gen_description"),
                "keywords", "in_sitemap"
            ],
            "classes": ("collapse-closed",)
        }),
    )

    inlines = [OccurrenceInline]

admin.site.register(Event, EventAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
