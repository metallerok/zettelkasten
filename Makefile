SYSTEM_PYTHON=$(shell which python3 || shell which python)
PYTHON_VENV=.venv/bin/python
PYTHON=$(shell if test -f ${PYTHON_VENV}; then echo ${PYTHON_VENV}; else echo ${SYSTEM_PYTHON}; fi)

install: requirements.txt
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -x -s -vvv

migrate_up:
	$(PYTHON) -m alembic upgrade head

migrate_down:
	$(PYTHON) -m alembic downgrade -1

migration:
	$(PYTHON) -m alembic revision --autogenerate -m $(name)

run_web:
	$(PYTHON) -m gunicorn -c gunicorn.conf.py 'src.entrypoints.web.wsgi:make_app()'

docker_build:
	docker build -t zettelkasten-web -f docker/web/Dockerfile .

docker_up:
	docker compose -f docker/docker-compose.dev.yml up

docker_down:
	docker compose -f docker/docker-compose.dev.yml down

docker_test:
	docker compose -f docker/docker-compose.dev.yml exec -it zettelkasten-web make test

docker_migrate_up:
	docker compose -f docker/docker-compose.dev.yml exec -it zettelkasten-web make migrate_up

docker_migrate_down:
	docker compose -f docker/docker-compose.dev.yml exec -it zettelkasten-web make migrate_down

run_celery_workers:
	$(PYTHON) -m celery --app src.entrypoints.celery.app worker -c 2 --loglevel=info

run_celery_beat:
	$(PYTHON) -m celery --app src.entrypoints.celery.app beat --loglevel=info
