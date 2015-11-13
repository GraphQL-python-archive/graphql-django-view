SECRET_KEY = 1
INSTALLED_APPS = []
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'graphql_django_view.testenv.urls'
