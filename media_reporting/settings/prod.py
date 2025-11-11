from .base import *
import os
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "report.stpprojects.in",
    "www.report.stpprojects.in",
]

CSRF_TRUSTED_ORIGINS = [
    "https://report.stpprojects.in",
    "http://report.stpprojects.in",
    "https://www.report.stpprojects.in",
]

# ✅ Important for Cloudflare Tunnel — tells Django that HTTPS is handled by proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ✅ Database (PostgreSQL via docker-compose)
DATABASES = {
    "default": env.db("DATABASE_URL")
}

# ✅ Optional: redirect all HTTP → HTTPS automatically
SECURE_SSL_REDIRECT = True
# Whitenoise: enable gzip and cache-busting for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
