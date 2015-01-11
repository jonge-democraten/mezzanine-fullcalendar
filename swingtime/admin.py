from django.contrib import admin
from swingtime.models import *

class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class OccurrenceInline(admin.TabularInline):
    model = Occurrence
    extra = 1


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_category')
    list_filter = ('event_category',)
    search_fields = ('title', 'description', 'content', 'keywords')
    exclude = ('slug', '_meta_title', 'gen_description', 'description')

    inlines = [OccurrenceInline]


admin.site.register(Event, EventAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
