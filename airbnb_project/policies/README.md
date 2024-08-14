# Policies App Testing Guide

This guide covers the steps to set up and test the Policies app.

## Step 1: Set Django Settings Module

Set `DJANGO_SETTINGS_MODULE` in poetry shell

```sh
DJANGO_SETTINGS_MODULE=airbnb_project.settings_test
```

## Step 2: Create & Apply Migrations for Listings and Policies Apps

Make sure you have models in both the listings and policies apps. Then, create and apply migrations for listings app, following by policies app:

```sh
python manage.py makemigrations listings
python manage.py migrate listings

```
```sh
python manage.py makemigrations policies
python manage.py migrate policies

```

## Step 3: Running Tests

Run the tests for the Policies app to ensure everything is set up correctly:

```sh
python manage.py test policies
```
Example output when all tests passed:

```sh
Found 5 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.....
----------------------------------------------------------------------
Ran 5 tests in 0.044s

OK
Destroying test database for alias 'default'...
```