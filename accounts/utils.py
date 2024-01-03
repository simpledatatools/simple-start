from django.conf import settings
import string
import random

from .models import MailLinkModel
from messaging.tasks import send_email

# Creates in initial username with random characters (not currently used)
def create_username(name):
        name = name.replace(" ", "")
        choices = string.ascii_letters + string.hexdigits
        choice = "".join(random.choice(choices) for _ in range(10))
        username = f'{name}{choice}'
        return username


def create_link(link_for: str):
    choice = string.ascii_letters + string.digits
    key = "".join(random.choice(choice) for _ in range(30))
    if link_for == 'sign-up':
        link = f"{settings.BASE_URL}verify?key={key}"
    elif link_for == 'reset-password':
        link = f"{settings.BASE_URL}forgot-password?key={key}"
    return link, key


def send_user_verification(user):
    # Create a verification link to confirm their email
    link, key = create_link(link_for='sign-up')
    obj, created = MailLinkModel.objects.update_or_create(user=user, link_type="register", is_delete=False)
    obj.key = key
    obj.save()
    # Send email out using celery

    send_email.delay(recipient_name=user.first_name, link=link, recipient_list=user.email, subject="Verify your Simple Start account", mail_for="sign-up", body=None)