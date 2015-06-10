# Django settings for lab51 project.

import os, sys
import os.path

HATCHING = False


PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'production')

DATABASES = { 'hacking':'lab51B_db', 'default':'lab51F_db'}

sys.path.append(PROJECT_ROOT_PATH)

if DJANGO_ENV == 'production':
    ## print >>sys.stderr, "PRODUCTION!"
    DEBUG = False
else:
    ## print >>sys.stderr, "DEVELOPMENT!"
    DEBUG = True

# for now, always debug templates
os.environ['DJANGO_DB_POOL'] = DEBUG and 'FALSE' or 'TRUE'
TEMPLATE_DEBUG = True
## DEBUG = False

FILESYSTEM_CACHE_PATH = os.environ.get('DJANGO_FILESYSTEM_CACHE',  '/Projects/junebug/CACHE')

if not os.environ.get('NOCACHE', False):
    CACHE_BACKEND_PATH = FILESYSTEM_CACHE_PATH + "/data"
    CACHE_BACKEND = 'file://' + CACHE_BACKEND_PATH + '?timeout=900'
    if not os.path.exists(CACHE_BACKEND_PATH):
        os.makedirs(CACHE_BACKEND_PATH, 0775)
    

ADMINS = (
    ('zookeeper', 'webfarmer@umich.edu'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = DATABASES.get(DJANGO_ENV, DATABASES['default'])             # Or path to database file if using sqlite3.
DATABASE_USER = 'biokids'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Detroit'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT_PATH

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(f49v)si)k)=a874d**i^%4ilrsdx#fa(g+@o$(6s&k=o!ol-z'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'vhost_middleware.VhostContextProcessor',
)

MIDDLEWARE_CLASSES = (
    'vhost_middleware.VhostMiddleware',
    'cybertracker_reports.filesystem_cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'cybertracker_reports.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT_PATH, 'templates'),
)

INSTALLED_APPS = (
    # 'cybertracker_reports.biokids',
    'cybertracker_reports.cybertracker',
    'django.contrib.auth',
    'modify_user_class',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.markup',
    'django.contrib.admin',
)
