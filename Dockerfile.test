# Docker image for testing only
#
FROM debian:buster-slim

RUN apt-get update -y && apt-get install -y \
    python3-pip \
    python3-dev

RUN useradd asterisk

COPY . /app
WORKDIR /app

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -e .[dev] && \
    python3 -m pip install -e .
