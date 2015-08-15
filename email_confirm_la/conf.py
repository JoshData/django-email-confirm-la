# coding: utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from appconf import AppConf


class ECLAAppConf(AppConf):
    EMAIL_BACKEND = settings.EMAIL_BACKEND
    CONFIRM_EXPIRE_SEC = 60 * 60 * 24 * 1  # 1 day
    KEY_LENGTH = 16

    class Meta:
        prefix = 'email_confirm_la'

