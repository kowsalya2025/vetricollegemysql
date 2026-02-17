import pymysql
pymysql.install_as_MySQLdb()
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.VERSION = (2, 2, 1)

from pathlib import Path
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# DJANGO_SECRET_KEY='django-insecure-l!2jv%k&ogob=b1a)93y(q0h$8$#csjiwikt=oq0y!g!c*&w+l'


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY is not set")




# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    "vetricollege.onrender.com",
    "localhost",
    "127.0.0.1",
    ".onrender.com",
]






# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage', 
    'django.contrib.staticfiles',
    'django.contrib.sites', 
     'cloudinary',
    # Required for allauth

    # Third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'ckeditor',
   

    # Local apps
    'lms',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',

]

ROOT_URLCONF = 'lms_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'lms_project.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST", "localhost"),
        'PORT': os.getenv("DB_PORT", "3306"),
    }
}




# Custom User Model
AUTH_USER_MODEL = 'lms.User'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True




# Media files (User uploaded content)
MEDIA_ROOT = '/media'
MEDIA_ROOT = BASE_DIR / 'media'


CKEDITOR_UPLOAD_PATH = "uploads/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Django Allauth Settings
# ===== ALLAUTH SETTINGS =====
# Configure allauth to work with email-only authentication
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Users log in with email
ACCOUNT_EMAIL_REQUIRED = True  # Email is required
ACCOUNT_USERNAME_REQUIRED = False  # Username is NOT required
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # No username field
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Can be 'mandatory', 'optional', or 'none'
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False  # Don't ask for password twice
ACCOUNT_SESSION_REMEMBER = True  # Remember login
ACCOUNT_UNIQUE_EMAIL = True  # Ensure emails are unique
ACCOUNT_LOGOUT_ON_GET = True  # Logout on GET request

# ===== SOCIAL ACCOUNT SETTINGS =====
SOCIALACCOUNT_AUTO_SIGNUP = True  # Automatically create users from social logins
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Skip email verification for social accounts
SOCIALACCOUNT_EMAIL_REQUIRED = True  # Email is required
SOCIALACCOUNT_QUERY_EMAIL = True  # Request email from social providers
SOCIALACCOUNT_STORE_TOKENS = True  # Store OAuth tokens

# IMPORTANT: Tell allauth to skip the username
SOCIALACCOUNT_FORMS = {
    'signup': 'lms.forms.CustomSocialSignupForm',
}

# Or if you don't want to create forms.py, use:
SOCIALACCOUNT_ADAPTER = 'lms.adapters.CustomSocialAccountAdapter'


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
# Stripe Configuration

# settings.py


# ===== GOOGLE OAUTH =====
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
        }
    }
}

# Messages framework
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'



# Email Settings (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv("CLOUDINARY_CLOUD_NAME"),
    'API_KEY': os.getenv("CLOUDINARY_API_KEY"),
    'API_SECRET': os.getenv("CLOUDINARY_API_SECRET"),
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
else:
    # Development settings - no SSL
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')


