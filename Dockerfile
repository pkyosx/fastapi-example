# first stage
FROM python:3.10.10-slim

RUN apt update && apt install -y \
    gcc \
    libpq-dev \
    postgresql-client

WORKDIR /workspace
COPY requirements.txt /workspace
RUN pip install -r requirements.txt

COPY . /workspace/
ENV PYTHONPATH /workspace/fastapi_example

CMD [ "sleep", "infinity" ]
