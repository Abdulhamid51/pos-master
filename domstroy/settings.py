from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "hxh%w6ctynfa8^cg$wo!fdn=bz7z=6x5(m_w)h9slyan4e3dpl"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "api",
    "main",
    "rest_framework",
    "rest_framework.authtoken",
    # sms send
    "django_crontab",
    "import_export",
    'tg_bot',
    "mathfilters", #pip install django-mathfilters
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'domstroy.middleware.LogRequestMiddleware',

]

ROOT_URLCONF = "domstroy.urls"
import os
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates", os.path.join(BASE_DIR, 'main/templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'main.context_processors.add_custom_data',
                'main.context_processors.course_context',

            ],
        },
    },
]

WSGI_APPLICATION = "domstroy.wsgi.application"



DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'ecomaruf',
#         'USER': 'ecomaruf',
#         'PASSWORD': 'password',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }


DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000000


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ("rest_framework.filters.SearchFilter",),
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
}

CRONJOBS = [
    ('0 4 * * 1-6', 'main.views.schedular_sms_send'), #
    ('02 19 * * *', 'api.views.all_day_sum_employee'), #
    ('39 18 * * *', 'api.views.all_day_sum_employee'), #
    ('2 19 * * *', 'api.views.add_daliy_rests'), #
    # ('05 12 * * *', 'api.views.all_day_sum_employee'), #
    # # ('0 14 * * 1-6', 'main.views.schedular_sms_send_olds'), #At 14:00 on every day-of-week from Monday through Saturday bir sms jo'natadi Qarzi utib ketganlarga
    # (
    #     "0 0 * * *","main.views.schedular_sms_send",
    # ),  # 6sotda. bir sms jo'natadi qarz kui kelganlarga
    # (
    #     "0 1 * * *","main.views.schedular_sms_send_olds",
    # ),  # 7 sotda bir sms jo'natadi Qarzi utib ketganlarga
    # (
    #     "0 2 * * *","main.views.schedular_sms_send_alert",
    # ),  # 8 sotda bir sms 3kun qolganida jo'natadi Qarzi utib ketganlarga
    # # ('*/1 * * * *', 'main.views.schedular_sms_send'),  # 1 min bir sms jo'natadi test qarz kui kelganlarga
    # # ('*/2 * * * *', 'main.views.schedular_sms_send_olds')  # 2 min bir sms jo'natadi test old
]

# Qarzini  tulaganida    sms jo'natadi

# RETURN_DEBTOR_SMS = "Qarzini berdi"
RETURN_DEBTOR_SMS = """
Assalom alaykum xurmatli {name} siz {som} so'm to'lov amalga oshirganingizni ma'lum qilamiz.
Qoldiq summa {qoldi} so'm

Xurmat bilan Bordo jamoasi!

Murojaat uchun: +998901254042
"""

# Qarziniga olsa sms jo'natadi
# GET_DEBTOR_SMS = "Assalom alaykum xurmatli {name} siz Bordo jamoasi do'konidan {som} so'm qarzdor bo'lganingizni ma'lum qilamiz. To'lov muddati {kun} gacha belgilandi, tolovni kechiktirmaysiz degan umitdamiz. Siz bilan hamkorlik qilayotganimizidan hursandmiz. Xurmat bilan Bordo jamoasi!  Murojat uchun:  +998901254042 "

GET_DEBTOR_SMS = """
Assalom alaykum
Xurmatli {name}
Bugunlik savdo {som} sum
Qoldiq {qoldiq} sum.
Siz bilan xamkorlik qilayotganimizdan mamnunmiz!!!
+998910197071
+998770195354
+998991254042
"""

# Deadline sms
DEADLINE_SMS = """
Assalom alaykum xurmatli {name} sizni Bordo jamoasi do'konidagi QARZ muomilangiz muddati kelgani  malum qilamiz, iltimos tulovni amalga oshiring.
Bu orqali siz, hamkorligimizni uzoq davom etishini taminlagan bo'lasiz.

Xurmat bilan Bordo jamoasi!

Murojat uchun:
+998901254042
"""

# Qarz kunidan utib ketdi
OLD_DEADLINE_SMS = """
Assalom alaykum xurmatli {name} sizni Bordo jamoasi do'konidagi QARZ muomilangiz muddati o'tib ketganini ma'lum qilamiz, iltimos to'lovni amalga oshiring.
Bu orqali siz, hamkorligimizni uzoq davom etishini taminlagan bo'lasiz.

Xurmat bilan Bordo jamoasi!

Murojat uchun:
+998901254042
"""

# 3day ago alert sms
THREE_DAY_AGO_SMS = """
Assalom alaykum xurmatli {name} sizni to'lov muddatingizga 3 kun qolganini eslatib o'tamiz
Iltimos tulovni kechiktirmay amalga oshirishingizni so'raymiz!!!
Summa {som} so'm

Xurmat bilan Bordo jamoasi!

Murojat uchun: +998901254042
"""

# CRONTAB_COMMAND_SUFFIX = '2>&1'
LANGUAGE_CODE = "uz-uz"

TIME_ZONE = "Asia/Tashkent"

# DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

USE_I18N = True

USE_L10N = False

USE_TZ = False

LOGIN_URL = "/login"

TELEGRAM_BOT_TOKEN = '8189365368:AAHzo5WFAtZSTrOm661At2z8rq-B_LXUSp8'


#sms
SMS_EMAIL = 'abdullox19990604@gmail.com'
SMS_SECRET_KEY = 'dfSkYkW7ypJdJHUhTdNJbOA1EIIddzTToUoJ5blJ'
SMS_BASE_URL = 'http://notify.eskiz.uz'
SMS_TOKEN = ''

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "assets"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# CORS_ALLOWED_ORIGINS = [
#     "http://104.236.200.53"
# ]
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = (
    "x-requested-with",
    "accept",
    "origin",
    "authorization",
    "x-csrftoken",
    "token",
    "x-device-id",
    "x-device-type",
    "x-push-id",
    "dataserviceversion",
    "maxdataserviceversion",
)
CORS_ALLOW_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")



TELEGRAM_GROUP_ID = '-1002061163231'
BOT_TOKEN = '6733642026:AAFuWM8ZJLCpEAZO9iDGJzThv9D-Uh_zgf4'
