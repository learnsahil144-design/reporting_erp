from .base import *
import os
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CSRF_TRUSTED_ORIGINS = [
    "https://report.stpprojects.in",
]

DATABASES = {
    "default": env.db("DATABASE_URL")
}
