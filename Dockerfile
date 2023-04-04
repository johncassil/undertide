FROM python:3.11-slim-bullseye

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git openssh-client libpq-dev gcc build-essential;

RUN mkdir /root/.ssh && touch /root/.ssh/known_hosts
RUN ssh-keyscan github.com>> /root/.ssh/known_hosts

ARG THE_ENV
ENV THE_ENV=${THE_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.4.1

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY poetry.lock pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$THE_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

COPY . ./

ENV PORT 8080
EXPOSE $PORT
CMD exec gunicorn --bind :$PORT --chdir /app/undertide --workers 1 --threads 8 --timeout 0 main:app
