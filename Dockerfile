FROM python:3.8-slim

ENV GIT_DISCOVERY_ACROSS_FILESYSTEM=1
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y make

RUN pip install poetry && \
    pip install psycopg2-binary

WORKDIR /workspaces/Matroskin