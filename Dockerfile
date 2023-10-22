# first stage
FROM python:3.10.10-slim

WORKDIR /workspace/fastapi_example
COPY . /workspace
RUN pip install -e /workspace/.[test]
ENV PYTHONPATH /workspace/fastapi_example

ENTRYPOINT ["gunicorn", "main:app"]
