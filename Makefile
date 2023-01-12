SYSTEM_PYTHON=$(shell echo $(shell which python3) || $(shell which python))
PYTHON_VENV=.venv/bin/python
PYTHON=$(shell if test -f ${PYTHON_VENV}; then echo ${PYTHON_VENV}; else echo ${SYSTEM_PYTHON}; fi)

install: requirements.txt
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -x -x -vvv

run web:
	$(PYTHON) -m gunicorn -c gunicorn.conf.py 'src.entrypoints.web.wsgi:make_app()'

docker build:
	docker build -t zettelkasten-web -f docker/web/Dockerfile .

docker up:
	docker compose -f docker/docker-compose.dev.yml up

docker down:
	docker compose -f docker/docker-compose.dev.yml down
