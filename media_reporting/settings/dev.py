from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Use databases from base.py (Postgres)
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:4000",
    "http://127.0.0.1:4000",
]