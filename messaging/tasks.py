from celery import shared_task
from .mail_utils import SendMail
from django.core.mail import send_mail

import logging
logger = logging.getLogger('SimpleStart')

@shared_task(name="Send Email")
def send_email(
    mail_for,
    recipient_name, 
    link,
    recipient_list,
    subject,
    body):

    mail = SendMail(
        mail_for=mail_for,
        recipient_name=recipient_name,
        link=link,
        recipient_list=recipient_list,
        subject=subject,
        body=body,
    )
    status = mail.send()
    
    return True

@shared_task(name="Send General Email")
def send_general_email(to, subject, message):
    logger.info(to)
    logger.info(subject)
    logger.info(message)
    try:
        send_mail(subject=subject, message=message, from_email='Simple Start <hello@support.simpledatatools.com>', recipient_list=[to], fail_silently=True)
        return True
    except Exception:
        return False