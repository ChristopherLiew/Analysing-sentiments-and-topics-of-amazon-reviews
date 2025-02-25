###############################################
# Base Image                                  #
###############################################
FROM python:3.8-slim as python-base

ENV PYTHONUNBUFFERED=1\
    PYTHONDONTWRITEBYTECODE=1\
    PIP_NO_CACHE_DIR=off\
    PIP_DISABLE_PIP_VERSION_CHECK=on\
    PIP_DEFAULT_TIMEOUT=100\
    POETRY_VERSION=1.1.6\
    POETRY_HOME="/opt/poetry"\ 
    POETRY_VIRTUALENVS_IN_PROJECT=true\
    POETRY_NO_INTERACTION=1\
    PYSETUP_PATH="/opt/pysetup"\
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

###############################################
# Builder Image                               #
###############################################
FROM python-base as builder-base
RUN apt-get update\
    && apt-get install --no-install-recommends -y\
    curl\
    build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
# Disable new poetry installer
RUN poetry config experimental.new-installer false

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev

###############################################
# Production Image                            #
###############################################
FROM python-base as production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY . /src/

# References:
# https://www.mktr.ai/the-data-scientists-quick-guide-to-dockerfiles-with-examples/
# https://github.com/michael0liver/python-poetry-docker-example/blob/master/docker/Dockerfile
# Dockerfile TUtorial
# https://www.youtube.com/watch?v=6Er8MAvTWlI
