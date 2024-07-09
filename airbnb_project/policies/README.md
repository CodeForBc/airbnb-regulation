# Policies App Testing Guide

This guide covers the steps to set up and test the Policies app using a PostgreSQL database.


## Step 1: Create PostgreSQL Database

1. Log in to your PostgreSQL database as a superuser:

    ```sh
    psql -U postgres
    ```

2. Create a new user and a new database for testing:
  
    ```sql
    CREATE USER test_db_user WITH PASSWORD 'your_password_here';
    CREATE DATABASE test_db_name;
    ALTER USER test_db_user CREATEDB;
    GRANT ALL PRIVILEGES ON DATABASE test_db_name TO test_db_user;
    ```
    Note that `test_db_user`, `test_db_name` are set to `admin`, `airbnb_db` by default in `settings_test.py`

## Step 2: Create a `.env` File

Create a `.env` file in the root directory of your project with the following content:

```plaintext
TEST_DB_PASSWORD=your_password_here
```

## Step 3: Check Database Config in `settings_test.py`
Make sure the `DATABASES` is set as:

```python
DATABASES['default']['NAME'] = 'airbnb_db'
DATABASES['default']['USER'] = 'test_db_name'
DATABASES['default']['PASSWORD'] = os.environ['TEST_DB_PASSWORD']
DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = '5432'
```

## Step 4: Set Django Settings Module

Set `DJANGO_SETTINGS_MODULE` in poetry shell

```sh
DJANGO_SETTINGS_MODULE=airbnb_project.settings_test
```

## Step 5: Create & Apply Migrations for Listings and Policies Apps

Make sure you have models in both the listings and policies apps. Then, create and apply migrations for listings app, following by policies app:

```sh
python manage.py makemigrations listings
python manage.py migrate listings

```
```sh
python manage.py makemigrations policies
python manage.py migrate policies

```

## Step 6: Running Tests

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