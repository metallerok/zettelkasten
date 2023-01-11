FROM python:3.8-alpine as builder

COPY requirements.txt .

RUN apk update \
    && apk add --no-cache postgresql-dev python3-dev build-base libffi-dev openssl-dev zlib-dev jpeg-dev\
    && pip install --user -r requirements.txt


FROM python:3.8-alpine
WORKDIR /opt/app/backend

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local:$PATH

COPY . .

CMD ["make", "run_web"]
#CMD ["gunicorn", "-c", "gunicorn.conf.py", "src.entrypoints.web.wsgi:make_app()"]
