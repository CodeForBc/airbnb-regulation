# Policy Processor Testing Guide

This guide covers the steps to set up and test the Policy Processor

## Step 1: Set Django Settings Module

Set `DJANGO_SETTINGS_MODULE` in poetry shell

```sh
DJANGO_SETTINGS_MODULE=airbnb_project.settings_test
```

## Step 2: Create & Apply Migrations for Listings and Policy Processor

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
 
## API Documentation

### Policy Processor Listings Endpoint

This endpoint triggers the process of evaluation of Airbnb listings data against the policies.
You'd want to run the harvester endpoint first and use the date from harvester run in the query param below.

- **URL**: `/policies/evaluate-policies/?scrapped_at=<YYYY-MM-DD>`
- **Method**: `GET`
- **Success Response**:
    - **Code**: 200
    - **Content**: Policy Evaluation Finished - Total `<Count>` listings evaluated successfully. Failed: `<Count>`
- **Error Responses**:
    - **Code**: 500
        - **Content**: Internal server error during policy evaluation

Example usage with `curl`:

```bash
curl http://localhost:8000/policies/evaluate-policies/?scrapped_at=<YYYY-MM-DD>
```