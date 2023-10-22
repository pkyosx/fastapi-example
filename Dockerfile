# first stage
FROM python:3.10.10-slim

WORKDIR /workspace
COPY requirements.txt /workspace
RUN pip install -r requirements.txt

COPY . /workspace/
ENV PYTHONPATH /workspace/fastapi_example

CMD [ "sleep", "infinity" ]
