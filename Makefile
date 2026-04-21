install:
	pip install -e src

run:
	python src/app/main.py

unit-test:
	pytest src/tests/unit