import os
from pathlib import Path
import dj_database_url  

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-wp_v(2z00ec3zhng&t5gs6@*y6-x7&(b=)n9%8ir^(9v5mxb2&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://chattig-app.onrender.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Video_Platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.notification_badge',
            ],
        },
    },
]

WSGI_APPLICATION = 'Video_Platform.wsgi.application'

# =========================
# ✅ ImageKit Configuration
# =========================


# ========================
# ✅ Database (SQLite or Postgres)
# ========================

DATABASES = {
    'default': dj_database_url.parse(
        "postgresql://database_r559_user:73DnZGSNapxNj189ZU2Sx68MdszP0Yl0@dpg-d1ahjg3e5dus73eju4dg-a.oregon-postgres.render.com/database_r559"
    )
}
# ========================
# ✅ Password Validation
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================
# ✅ Internationalization
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========================
# ✅ Static Files
# ========================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# ========================
# ✅ Media (only if needed)
# ========================
# You won't use MEDIA_URL/MEDIA_ROOT if uploading directly to ImageKit.
# But keeping this in case you use local media during development.
NEXTCLOUD_BASE_URL = 'https://tio.lv.tab.digital/remote.php/dav/files/samarth172024%40gmail.com/django_media/'
NEXTCLOUD_USERNAME = 'samarth172024@gmail.com'
NEXTCLOUD_PASSWORD = 'samarth172024@gmail.com'  

NEXTCLOUD_PUBLIC_BASE = 'https://tio.lv.tab.digital/s/yGRxgDZM8iNa6qc/download?path=/'

# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# ========================
# ✅ Auto Field
# ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
