FROM python:3.11-slim-bullseye

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git openssh-client;

RUN mkdir /root/.ssh && touch /root/.ssh/known_hosts
RUN ssh-keyscan github.com>> /root/.ssh/known_hosts

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN --mount=type=ssh pip install -r requirements.txt

EXPOSE 8080
CMD exec gunicorn --bind :$PORT --chdir /undertide/app/src --workers 1 --threads 8 --timeout 0 main:app
