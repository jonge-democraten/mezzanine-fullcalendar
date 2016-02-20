# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ('-publish_date',), 'verbose_name_plural': 'events', 'verbose_name': 'event'},
        ),
        migrations.AlterField(
            model_name='event',
            name='publish_date',
            field=models.DateTimeField(db_index=True, blank=True, verbose_name='Published from', null=True, help_text="With Published chosen, won't be shown until this time"),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='publish_date',
            field=models.DateTimeField(db_index=True, blank=True, verbose_name='Published from', null=True, help_text="With Published chosen, won't be shown until this time"),
        ),
    ]
