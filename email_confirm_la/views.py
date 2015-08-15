# coding: utf-8

from django.shortcuts import render
from email_confirm_la.models import EmailConfirmation
from email_confirm_la.exceptions import EmailConfirmationExpired

def confirm_email(request, confirmation_key):
    # Get the EmailConfirmation object for this key.
    try:
        email_confirmation = EmailConfirmation.objects.get(confirmation_key=confirmation_key)
    except (EmailConfirmation.DoesNotExist, EmailConfirmationExpired):
        # The key is invalid, which means it probably expired.
        return render(request, 'email_confirm_la/email_confirm_fail.html', context)

    # Confirm the email address.
    email_confirmation.confirm(request)

    # Get any object-specific response view.
    response = email_confirmation.view_func(request)
    if response:
        return response

    # Render the default view.
    return render(request, 'email_confirm_la/email_confirm_success.html', {
        'email_confirmation': email_confirmation,
    })
