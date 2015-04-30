# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20150321_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventcategory',
            name='name',
            field=models.CharField(max_length=50, verbose_name='name'),
            preserve_default=True,
        ),
    ]
