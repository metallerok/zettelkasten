FROM python:3.10-slim as celery_builder

COPY requirements.txt .

RUN apt update \
    && apt install -y make libpq-dev gcc\
    && pip install --user -r requirements.txt


FROM celery_builder
WORKDIR /opt/app/backend

COPY . .

RUN cp config.py.example config.py

CMD ["make", "run_celery"]
