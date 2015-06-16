# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('keywords_string', models.CharField(editable=False, max_length=500, blank=True)),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('slug', models.CharField(help_text='Leave blank to have the URL auto-generated from the title.', null=True, max_length=2000, blank=True, verbose_name='URL')),
                ('_meta_title', models.CharField(help_text='Optional title to be used in the HTML title tag. If left blank, the main title field will be used.', null=True, max_length=500, blank=True, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('gen_description', models.BooleanField(help_text='If checked, the description will be automatically generated from content. Uncheck if you want to manually set a custom description.', default=True, verbose_name='Generate description')),
                ('created', models.DateTimeField(editable=False, null=True)),
                ('updated', models.DateTimeField(editable=False, null=True)),
                ('status', models.IntegerField(help_text='With Draft chosen, will only be shown for admin users on the site.', choices=[(1, 'Draft'), (2, 'Published')], default=2, verbose_name='Status')),
                ('publish_date', models.DateTimeField(help_text="With Published chosen, won't be shown until this time", null=True, blank=True, verbose_name='Published from')),
                ('expiry_date', models.DateTimeField(help_text="With Published chosen, won't be shown after this time", null=True, blank=True, verbose_name='Expires on')),
                ('short_url', models.URLField(null=True, blank=True)),
                ('in_sitemap', models.BooleanField(default=True, verbose_name='Show in sitemap')),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
            ],
            options={
                'verbose_name_plural': 'events',
                'ordering': ('title',),
                'verbose_name': 'event',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('description', models.CharField(null=True, max_length=255, blank=True, verbose_name='description')),
                ('color', models.CharField(null=True, max_length=10, blank=True, verbose_name='color')),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'event categories',
                'verbose_name': 'event category',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('keywords_string', models.CharField(editable=False, max_length=500, blank=True)),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('slug', models.CharField(help_text='Leave blank to have the URL auto-generated from the title.', null=True, max_length=2000, blank=True, verbose_name='URL')),
                ('_meta_title', models.CharField(help_text='Optional title to be used in the HTML title tag. If left blank, the main title field will be used.', null=True, max_length=500, blank=True, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('gen_description', models.BooleanField(help_text='If checked, the description will be automatically generated from content. Uncheck if you want to manually set a custom description.', default=True, verbose_name='Generate description')),
                ('created', models.DateTimeField(editable=False, null=True)),
                ('updated', models.DateTimeField(editable=False, null=True)),
                ('status', models.IntegerField(help_text='With Draft chosen, will only be shown for admin users on the site.', choices=[(1, 'Draft'), (2, 'Published')], default=2, verbose_name='Status')),
                ('publish_date', models.DateTimeField(help_text="With Published chosen, won't be shown until this time", null=True, blank=True, verbose_name='Published from')),
                ('expiry_date', models.DateTimeField(help_text="With Published chosen, won't be shown after this time", null=True, blank=True, verbose_name='Expires on')),
                ('short_url', models.URLField(null=True, blank=True)),
                ('in_sitemap', models.BooleanField(default=True, verbose_name='Show in sitemap')),
                ('start_time', models.DateTimeField(verbose_name='start time')),
                ('end_time', models.DateTimeField(verbose_name='end time')),
                ('location', models.CharField(null=True, max_length=255, blank=True, verbose_name='location')),
                ('event', models.ForeignKey(verbose_name='event', editable=False, to='events.Event')),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'occurrences',
                'ordering': ('start_time', 'end_time'),
                'verbose_name': 'occurrence',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='event_category',
            field=models.ForeignKey(blank=True, verbose_name='event category', null=True, to='events.EventCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='site',
            field=models.ForeignKey(editable=False, to='sites.Site'),
            preserve_default=True,
        ),
    ]
