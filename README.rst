django-email-confirm-itf
========================

Django email confirmation for any model with simple callbacks. Based originally on `django-email-confirm-la <https://github.com/vinta/django-email-confirm-la>`_. For Python 3/Django 1.7+.

Installation
============

In your ``settings.py``:

Add the ``email_confirm_la`` app (put it *after* your apps) and set the required settings:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'email_confirm_la',
        ...
    )

    DEFAULT_FROM_EMAIL = 'hello@your-domain.com'
    SITE_ROOT_URL = 'https://yoursite.com' # no trailing slash!

In your ``urls.py``:

.. code-block:: python

    urlpatterns = patterns(
        '',
        url(r'^ev/', include('email_confirm_la.urls')),
        ...
    )

which creates a short path for email confirmation return URLs, but you can set `ev` to anything.

then run

.. code-block:: bash

    $ python manage.py migrate

to create the database table.

Models
======

For User Model
==============

.. code-block:: python

    from django.contrib.auth.models import User
    from email_confirm_la.models import EmailConfirmation

    user = User.objects.get(username='vinta')
    unconfirmed_email = 'vinta.chen@gmail.com'

    email_confirmation = EmailConfirmation.create(user, email=unconfirmed_email)
    email_confirmation.send()

When the user clicks the confirmation link in the sent email, the 'email' field on the User object will be filled in and saved. For other models, you might need to set the ``email_field_name`` keyword argument to ``create`` to something other than ``"email"``.

The user will be shown a simple confirmation page. To override that page, create a template at ``email_confirm_la/email_confirm_success.html`` (or see below for a more complex way).

Overriding Confirmation Behavior
================================

The default behavior is to save the email address directly into the object provided to ``create``. You can instead perform any function by defining a new method on your object, e.g.:

.. code-block:: python

class User(models.Model):
    ...


    def email_confirmation_confirmed(self, email_confirmation, request)
        self.email = email_confirmation.email
        self.save()

``email_confirmation`` is an email_confirm_la.EmailConfirmation instance, so you can see the source for other fields you could access here. ``request`` is the Django HttpRequest instance for the currently executing view, which allows you to use the Django messages framework, for instance.

In cases where you've saved the address in your own model and want to set a confirmed flag, you would do this:

.. code-block:: python
from django.contrib import messages

class Record(models.Model):
    email = models.EmailField(max_length=255)
    is_confirmed = models.BooleanField(default=False)

    def send_confirmation(self):
        email_confirmation = EmailConfirmation.create(self)
        email_confirmation.send()

    def email_confirmation_confirmed(self, email_confirmation, request)
        self.is_confirmed = True
        self.save()
        messages.add_message(request, messages.SUCCESS, 'You are confirmed.')

``email_confirmation_confirmed`` will be called at most once per confirmation.

Overring the Success View
=========================

The success view can be completely overridden by defining a ``email_confirmation_response_view`` instance method on your object. It is called immediately after ``email_confirmation_confirmed`` (or the default confirmation behavior), so you can assume the email address is already confirmed.

.. code-block:: python

class Record(models.Model):
    ...

    def email_confirmation_response_view(self, request):
        return HttpResponseRedirect(self.get_absolute_url())

This view may be called multiple times for the same confirmation, because users often mis-click and load email confirmation links more than once. 

Commands
========

.. code-block:: bash

    $ python manage.py clear_expired_email_confirmations

Templates
=========

You will want to override the project's email text and (if you haven't provided a response view) confirmation page.

Ensure the ``email_confirm_la`` app in ``INSTALLED_APPS`` is after the app that you will place the customized templates in so that the `django.template.loaders.app_directories.Loader <https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.app_directories.Loader>`_ finds *your* templates before the default templates.

Then copy the templates into your app:

.. code-block:: bash

    $ mkdir -p your_app/templates/email_confirm_la
    $ cp -R django-email-confirm-la/email_confirm_la/templates/email_confirm_la your_app/templates/email_confirm_la

Finally, modify them:

* ``email/email_confirmation_subject.txt``: Produces the subject line of the email.
* ``email/email_confirmation_message.html``: The HTML body of the email.
* ``email_confirm_success.html``: What the user sees after clicking a confirmation link (on success).
* ``email_confirm_fail.html:`` What the user sees after clicking a confirmation link that has expired or is invalid.

Settings
========

Default values of other app settings:

.. code-block:: python

    EMAIL_CONFIRM_LA_EMAIL_BACKEND = settings.EMAIL_BACKEND
    EMAIL_CONFIRM_LA_CONFIRM_EXPIRE_SEC = 60 * 60 * 24 * 1  # 1 day

Overriding How Mails Are Sent
=============================

You may pass a function as the optional `mailer` argument to `send`. If you do so, instead of sending an email using Django's built in template rendering and email methods, your mailer function will be called with a dict:

    {
        'email': "email-being-confirmed@domain.dom",
        'confirmation_key': "randomtexthere",
        'confirmation_url': "http://yoursite.com/path/to/confirm/url",
    }

You are then responsible for sending the email. ``email_confirmation_subject.txt`` and ``email_confirmation_message.html`` are not used in this case.
