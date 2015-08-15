# coding: utf-8

from django.db import transaction
import django


__all__ = ['transaction', 'update_fields']


if django.VERSION < (1, 6):
    transaction.atomic = transaction.commit_on_success

