import os

from .base import *

DEBUG = False

SECRET_KEY = os.environ["WAGTAIL_SECRET_KEY"]

# Derived from DOMAIN (provided by the lab's .env) → blog.<DOMAIN>.
BLOG_HOST = f"blog.{os.environ.get('DOMAIN', 'example.com')}"
ALLOWED_HOSTS = [BLOG_HOST]
CSRF_TRUSTED_ORIGINS = [f"https://{BLOG_HOST}"]

# nginx terminates TLS and proxies over http; trust its X-Forwarded-Proto so
# Django knows the original request was https (fixes admin-login CSRF + URLs).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Static files are served by WhiteNoise (see MIDDLEWARE in base.py).
# Compress without a strict manifest, so collectstatic (run under dev settings
# at build) doesn't have to produce a staticfiles.json.
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedStaticFilesStorage"

try:
    from .local import *
except ImportError:
    pass
