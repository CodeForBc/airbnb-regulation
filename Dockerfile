# References:
# Docker Best Practices from poetry: https://github.com/gianfa/poetry/blob/d12242c88edf1c8cf6d9aa70677beda212576760/docs/docker-best-practices.md

################################
# PYTHON-BASE
# Sets up all our shared environment variables
################################
# Use an official Python runtime as a parent image
FROM python:3.10-slim as python-base

ARG POETRY_VERSION=1.8

# Set environment variables
ENV PYTHONUNBUFFERED 1
# prevents python creating .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# pip
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100
# poetry
# make poetry install to this location
ENV POETRY_HOME=/opt/poetry
# make poetry create the virtual environment in the project's root
# it gets named `.venv`
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_VIRTUALENVS_CREATE=1
ENV POETRY_NO_INTERACTION=1
# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=/opt/.cache


################################
# BUILDER-BASE
# Used to build deps + create our virtual environment
################################
FROM python-base as builder-base

# Install system dependencies
RUN apt update \
    && apt install --no-install-recommends -y\
    curl \
    build-essential

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Install the dependencies and clear the cache afterwards.
#   This may save some MBs.
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

################################
# DEVELOPMENT
# Image used during development / testing
################################
FROM python-base as dev-base

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# will become mountpoint of our code
WORKDIR /app

# Copy project
COPY ./airbnb_project/ /app/airbnb_project/

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]