# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_confirm_la', '0003_auto_20150211_1943'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailconfirmation',
            options={'verbose_name': 'Email confirmation', 'verbose_name_plural': 'Email confirmations'},
        ),
        migrations.RenameField(
            model_name='emailconfirmation',
            old_name='send_at',
            new_name='sent_at',
        ),
        migrations.RemoveField(
            model_name='emailconfirmation',
            name='is_primary',
        ),
        migrations.RemoveField(
            model_name='emailconfirmation',
            name='is_verified',
        ),
        migrations.AddField(
            model_name='emailconfirmation',
            name='resent_at_latest',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='emailconfirmation',
            name='confirmation_key',
            field=models.CharField(verbose_name='Confirmation_key', unique=True, max_length=32),
        ),
    ]
