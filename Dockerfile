# first stage
FROM python:3.10-slim AS builder

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN $GITHUB_TOKEN

WORKDIR /build
ADD /app/requirements.txt /build
RUN apt-get update && apt-get install -y git

# Create virtual environment and use it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install -r /build/requirements.txt

# second stage
FROM python:3.10-slim

ARG BUILD_VERSION

RUN apt-get update; apt-get -y install curl redis-tools vim dnsutils iputils-ping lsof procps telnet

WORKDIR /app
ADD /app /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH /app

ENV DOCKER_IMAGE_BUILD_VERSION="$BUILD_VERSION"

ENTRYPOINT ["gunicorn", "main:app"]
