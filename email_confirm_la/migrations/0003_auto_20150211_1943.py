# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('email_confirm_la', '0002_auto_20141112_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailconfirmation',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 2, 11, 19, 43, 23, 624367, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailconfirmation',
            name='send_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
