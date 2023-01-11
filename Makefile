SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON = $(or $(wildcard .venv/bin/python), $(SYSTEM_PYTHON))

install: requirements.txt
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -x -x -vvv

run_web:
	$(PYTHON) -m gunicorn -c gunicorn.conf.py 'src.entrypoints.web.wsgi:make_app()'
