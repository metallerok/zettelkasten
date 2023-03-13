FROM python:3.8-slim as builder

COPY requirements.txt .

RUN apt update \
    && apt install -y make libmagic1 \
    && pip install --user -r requirements.txt


FROM builder
WORKDIR /opt/app/backend

COPY . .

RUN cp config.py.example config.py && cp gunicorn.conf.py.example gunicorn.conf.py

CMD ["make", "run_web"]
