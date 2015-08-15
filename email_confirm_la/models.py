import datetime
import string
import random

try:
    # Django 1.7+ compatibility
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey

from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage, get_connection
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import pgettext_lazy as _
from django.conf import settings as django_settings

from email_confirm_la.compat import transaction
from email_confirm_la.conf import settings
from email_confirm_la.exceptions import EmailConfirmationExpired

def _default_mailer(template_context):
    subject = render_to_string('email_confirm_la/email/email_confirmation_subject.txt', template_context)
    subject = ''.join(subject.splitlines())  # remove superfluous line breaks

    body = render_to_string('email_confirm_la/email/email_confirmation_message.html', template_context)

    message = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [template_context['email'], ])
    message.content_subtype = 'html'

    connection = get_connection(settings.EMAIL_CONFIRM_LA_EMAIL_BACKEND)
    connection.send_messages([message, ])

class EmailConfirmation(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    email_field_name = models.CharField(verbose_name=_('ec_la', 'Email field name'), max_length=32)

    email = models.EmailField(verbose_name=_('ec_la', 'Email'), max_length=255)
    confirmation_key = models.CharField(verbose_name=_('ec_la', 'Confirmation_key'), max_length=32, unique=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    resent_at_latest = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    send_count = models.IntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('ec_la', 'Email confirmation')
        verbose_name_plural = _('ec_la', 'Email confirmations')
        unique_together = (('content_type', 'object_id', 'email_field_name', 'email'), )

    def __unicode__(self):
        return 'EmailConfirmation(%s)' % self.email

    @staticmethod
    def get_for(content_object, email_field_name='email'):
        content_type = ContentType.objects.get_for_model(content_object)
        return EmailConfirmation.objects.get(
            content_type=content_type,
            object_id=content_object.id,
            email_field_name=email_field_name,
        )

    @staticmethod
    def create(content_object, email_field_name='email', email=None):
        # Create a new EmailConfirmation object.
        confirmation = EmailConfirmation()
        confirmation.content_object = content_object
        confirmation.email_field_name = email_field_name
        confirmation.email = email or getattr(content_object, email_field_name)

        # Generate a random key.
        key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(settings.EMAIL_CONFIRM_LA_KEY_LENGTH))
        confirmation.confirmation_key = key

        confirmation.save()
        return confirmation

    def get_confirmation_url(self):
        return \
            django_settings.SITE_ROOT_URL \
            + \
            reverse('confirm_email', kwargs={'confirmation_key': self.confirmation_key})

    def send(self, mailer=_default_mailer):
        # Create the template context for rendering the template for the email to send.
        # If the content_object provides template context variables, use it.
        template_context = { }
        if hasattr(self.content_object, 'email_confirmation_template_context'):
            template_context.update(self.content_object.email_confirmation_template_context)

        # Add the context variables we need.
        template_context.update({
            'email': self.email,
            'confirmation_key': self.confirmation_key,
            'confirmation_url': self.get_confirmation_url(),
        })

        # Send mail.
        mailer(template_context)

        # Mark message as sent.
        if self.sent_at is None:
            # On first send, set sent_at.
            self.sent_at = timezone.now()
        else:
            # On later sends, set resent_at_latest.
            self.resent_at_latest = timezone.now()
        self.send_count = self.send_count + 1
        self.save(update_fields=('sent_at', 'resent_at_latest', 'send_count'))

    def is_expired(self):
        expiration_time = self.sent_at + datetime.timedelta(seconds=settings.EMAIL_CONFIRM_LA_CONFIRM_EXPIRE_SEC)
        return expiration_time <= timezone.now()
    is_expired.boolean = True

    def confirm(self, request):
        if self.confirmed_at:
            # This has already been confirmed.
            return

        if self.is_expired():
            # Confirmation time period has expired.
            raise EmailConfirmationExpired()

        if self.content_object is None:
            # Content object was deleted.
            raise EmailConfirmationExpired()

        with transaction.atomic():
            # Mark this object as confirmed.
            self.confirmed_at = timezone.now()
            self.save(update_fields=('confirmed_at',))

            if hasattr(self.content_object, 'email_confirmation_confirmed'):
                # If the content object has a method to handle confirmations, call it.
                return self.content_object.email_confirmation_confirmed(self, request)
            else:
                # Otherwise use default behavior of writing to the email field.
                setattr(self.content_object, self.email_field_name, self.email)
                self.content_object.save(update_fields=(self.email_field_name,))

    def view_func(self, request):
        if hasattr(self.content_object, 'email_confirmation_response_view'):
            return self.content_object.email_confirmation_response_view(request)
        return None
