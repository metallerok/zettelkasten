install: requirements.txt
	.venv/bin/pip install -r requirements.txt

test:
	.venv/bin/pytest -x -s -vvv

run_web:
	.venv/bin/gunicorn -c gunicorn.conf.py 'src.entrypoints.web.wsgi:make_app()'
