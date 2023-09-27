setup: requirements.txt
	pip install -r requirements.txt

run:
	python -m ctrlability

debug:
	python -m ctrlability -log DEBUG