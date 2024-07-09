"""
Django settings for airbnb_project project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from .settings import *

# Override or add specific test settings here
DATABASES['default']['NAME'] = 'airbnb_db'
DATABASES['default']['USER'] = 'admin'
DATABASES['default']['PASSWORD'] = 'admin'
DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = '5432'


# Ensure this setting to indicate it's a test environment
DEBUG = False  # Set to True or False as per your testing needs

# Ensure this setting to indicate it's a test environment
DEBUG = False  # Set to True or False as per your testing needs