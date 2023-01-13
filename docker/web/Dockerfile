FROM python:3.8-alpine as builder

COPY requirements.txt .

RUN apk update \
    && apk add --no-cache build-base libffi-dev openssl-dev zlib-dev jpeg-dev gcc make \
    && pip install --user -r requirements.txt


FROM builder
WORKDIR /opt/app/backend

COPY . .

RUN cp config.py.example config.py && cp gunicorn.conf.py.example gunicorn.conf.py

CMD ["make", "run", "web"]
