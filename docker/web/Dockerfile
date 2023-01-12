FROM python:3.8-alpine as builder

COPY requirements.txt .

RUN apk update \
    && apk add --no-cache postgresql-dev python3-dev build-base \
    libffi-dev openssl-dev zlib-dev jpeg-dev build-base gcc make \
    && pip install --user -r requirements.txt


FROM builder
WORKDIR /opt/app/backend

COPY . .

RUN cp config.py.example config.py && cp gunicorn.conf.py.example gunicorn.conf.py

CMD ["make", "run_web"]
