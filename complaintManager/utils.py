from django.conf import settings
from django.template import Context, Template
from django.template.loader import get_template
import os

try:
    from sendgrid.helpers.mail import *
    import sendgrid
except ImportError as e:
    SENDGRID_AVAILABLE = False
else:
    SENDGRID_AVAILABLE = True


def send_email(complaint, is_initial):
    apikey = settings.SENDGRID_API_KEY

    if not SENDGRID_AVAILABLE or apikey is None:
        print(
            'Sendgrid not configured. Simulated sending email to {}'.format(
                complaint.informer.email))
        return

    if is_initial:
        t = get_template('complaintManager/email_initial.html')
    else:
        t = get_template('complaintManager/email_update.html')
    c = Context({'complaint': complaint})
    body = t.render(c)

    sg = sendgrid.SendGridAPIClient(apikey=apikey)
    from_email = Email("ranggarmaste@gmail.com")
    to_email = Email(complaint.informer.email)
    subject = "[Keluhan #" + str(complaint.pk) + "] - " + complaint.title
    content = Content("text/html", body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
