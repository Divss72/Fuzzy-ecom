STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
import os

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Settings for uploaded images
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Where to go after logging in/out
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'