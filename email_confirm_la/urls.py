from django.conf.urls import patterns, url

import email_confirm_la.views

urlpatterns = [
    url(r'^key/(?P<confirmation_key>\w+)/$', email_confirm_la.views.confirm_email, name='confirm_email'),
]