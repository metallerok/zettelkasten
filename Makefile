install: requirements.txt
	.venv/bin/pip install -r requirements.txt

test:
	.venv/bin/pytest -x -s -v