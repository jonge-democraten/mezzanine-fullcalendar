# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='occurrence',
            name='location',
            field=models.CharField(verbose_name='location', max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eventcategory',
            name='description',
            field=models.CharField(verbose_name='description', max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
