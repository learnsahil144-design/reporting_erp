import logging
from django.contrib.auth.signals import user_login_failed, user_logged_in, user_logged_out
from django.dispatch import receiver

# Define a logger
logger = logging.getLogger("reports.auth")

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username')
    ip = request.META.get('REMOTE_ADDR')
    logger.warning(f"FAILED LOGIN attempt for user '{username}' from IP {ip}")

@receiver(user_logged_in)
def log_user_logged_in(sender, user, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    logger.info(f"SUCCESSFUL LOGIN: user '{user.username}' from IP {ip}")

@receiver(user_logged_out)
def log_user_logged_out(sender, user, request, **kwargs):
    if user:
        logger.info(f"LOGOUT: user '{user.username}'")
