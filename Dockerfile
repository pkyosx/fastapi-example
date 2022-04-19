# first stage
FROM python:3.10-slim AS builder

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN $GITHUB_TOKEN

WORKDIR /build
COPY /app/requirements.txt /build

# Create virtual environment and use it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir -r /build/requirements.txt

# second stage
FROM python:3.10-slim

WORKDIR /app
COPY /app /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH /app

ENTRYPOINT ["gunicorn", "main:app"]
