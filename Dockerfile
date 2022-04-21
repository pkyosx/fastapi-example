# first stage
FROM python:3.10-slim

WORKDIR /workspace/app
COPY . /workspace
RUN pip install -e /workspace/.[test]
ENV PYTHONPATH /workspace/app

ENTRYPOINT ["gunicorn", "main:app"]
