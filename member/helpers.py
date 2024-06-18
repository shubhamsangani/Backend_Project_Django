from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import get_connection, EmailMultiAlternatives, BadHeaderError
from django.http import HttpResponse


def send_notifying_email(event):
    subject = "Reminder for your task"
    email_template_name = "member/notify.html"

    c = {
        'event': event,
    }
    html_content = render_to_string(email_template_name, c)
    text_content = strip_tags(html_content)

    try:
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            ['greenhealthawareness@gmail.com']
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
    return True