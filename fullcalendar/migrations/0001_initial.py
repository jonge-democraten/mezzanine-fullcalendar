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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('keywords_string', models.CharField(blank=True, max_length=500, editable=False)),
                ('title', models.CharField(verbose_name='Title', max_length=500)),
                ('slug', models.CharField(null=True, verbose_name='URL', blank=True, max_length=2000, help_text='Leave blank to have the URL auto-generated from the title.')),
                ('_meta_title', models.CharField(null=True, verbose_name='Title', blank=True, max_length=500, help_text='Optional title to be used in the HTML title tag. If left blank, the main title field will be used.')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('gen_description', models.BooleanField(verbose_name='Generate description', help_text='If checked, the description will be automatically generated from content. Uncheck if you want to manually set a custom description.', default=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('status', models.IntegerField(verbose_name='Status', choices=[(1, 'Draft'), (2, 'Published')], help_text='With Draft chosen, will only be shown for admin users on the site.', default=2)),
                ('publish_date', models.DateTimeField(null=True, verbose_name='Published from', blank=True, help_text="With Published chosen, won't be shown until this time")),
                ('expiry_date', models.DateTimeField(null=True, verbose_name='Expires on', blank=True, help_text="With Published chosen, won't be shown after this time")),
                ('short_url', models.URLField(null=True, blank=True)),
                ('in_sitemap', models.BooleanField(verbose_name='Show in sitemap', default=True)),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
                'ordering': ('title',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, verbose_name='name', max_length=50)),
                ('description', models.CharField(verbose_name='description', max_length=255)),
                ('color', models.CharField(null=True, verbose_name='color', blank=True, max_length=10)),
                ('site', models.ForeignKey(to='sites.Site', editable=False)),
            ],
            options={
                'verbose_name': 'event category',
                'verbose_name_plural': 'event categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(null=True, blank=True, max_length=100)),
                ('start_time', models.DateTimeField(verbose_name='start time')),
                ('end_time', models.DateTimeField(verbose_name='end time')),
                ('event', models.ForeignKey(to='events.Event', editable=False, verbose_name='event')),
            ],
            options={
                'verbose_name': 'occurrence',
                'verbose_name_plural': 'occurrences',
                'ordering': ('start_time', 'end_time'),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='event_category',
            field=models.ForeignKey(blank=True, null=True, verbose_name='event category', to='events.EventCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='site',
            field=models.ForeignKey(to='sites.Site', editable=False),
            preserve_default=True,
        ),
    ]
