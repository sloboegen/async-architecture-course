# syntax=docker/dockerfile:1

FROM python:3.11.2-slim-buster

# python:
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip:
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_ROOT_USER_ACTION=ignore \
    # poetry:
    POETRY_VERSION=1.8.0 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'


RUN mkdir -p $POETRY_CACHE_DIR && \
    mkdir -p $POETRY_CACHE_DIR/virtualenvs


RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
    bash \
    curl \
    libpq-dev \
    gcc \
    python-dev \
    make \
    # Install poetry (https://github.com/python-poetry/poetry).
    && curl -sSL 'https://install.python-poetry.org' | python - \
    && poetry --version \
    # Clear cache.
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*


# Install Python-dependencies.
COPY ./schema_registry /opt/schema_registry/
COPY ./tracker_service/poetry.lock ./tracker_service/pyproject.toml /opt/tracker_service/
RUN cd /opt/tracker_service && poetry install --only=main

WORKDIR /opt/tracker_service

COPY ./tracker_service/ /opt/tracker_service/

CMD [ "/bin/bash", "-c", "poetry run uvicorn src.app:get_app --factory --log-level=debug --host=0.0.0.0 --port=8080" ]
