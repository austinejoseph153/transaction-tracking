from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.conf import settings
from .models import Notification
from django.utils.translation import gettext_lazy as _

def send_notification(subject, message, recipient, user, email_type):
    """
    send email payment details
    @param subject
    @param message
    @param recipient
    @param user
    @param email_type
    """
    notification = Notification.objects.create(
        user=user,
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient = recipient,
        message = message,
        type=email_type
    )
    subject = _(subject)
    try:
        msg_html = render_to_string('transaction/emails/email.html', {"message":message, "full_name":user.get_full_name()})
        to_email = [recipient]
        with get_connection(
            settings.EMAIL_BACKEND
        ) as connection:
            msg = EmailMessage(subject=subject, body=msg_html, from_email=settings.DEFAULT_FROM_EMAIL,
                           to=to_email, cc=None, connection=connection)
            msg.content_subtype = 'html'
            msg.send()
            notification.sent = True
            notification.save()
            return notification
    except:
        return None
