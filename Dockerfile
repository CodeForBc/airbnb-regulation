# References:
# Docker Best Practices from poetry: https://github.com/gianfa/poetry/blob/d12242c88edf1c8cf6d9aa70677beda212576760/docs/docker-best-practices.md

################################
# PYTHON-BASE
# Sets up all our shared environment variables
################################
# Use an official Python runtime as a parent image
FROM python:3.10-slim AS python-base

# Set poetry version as ARG to minimize build time
ARG POETRY_VERSION=1.8.4
# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

################################
# BUILDER-BASE
# Used to build dependencies + create virtual environment
################################
FROM python-base AS builder-base

# Install system dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        build-essential \
        curl \
        libpq-dev \
        pkg-config \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Poetry ENV
ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/opt/.cache

RUN python -m pip install --upgrade pip && \
    python -m pip install "poetry==$POETRY_VERSION" && \
    poetry --version

# Set the working directory
WORKDIR /app

# Install system dependencies
# RUN apt update && apt install --no-install-recommends -y build-essential

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Install runtime dependencies and clear cache
RUN poetry install --no-root --with dev && \
    rm -rf "$POETRY_CACHE_DIR"

################################
# DEVELOPMENT
# Image used during development / testing
################################
FROM python-base AS dev-base

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder-base ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy project
COPY . .

# Set the working directory to the Django project folder
WORKDIR /app/airbnb_project

# Run the application
CMD ["python", "manage.py", "check"]