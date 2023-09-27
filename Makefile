install: requirements.txt
	pip install -r requirements.txt

run:
	python -m ctrlability

dev:
	python -m ctrlability -log DEBUG