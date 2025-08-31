install:
	# install packages
	pip install --upgrade pip && \
		pip install -r requirements.txt

format:
	# format code
	black **/*.py

lint:
	# run the linter
	pylint --disable=R,C **/*.py

test:
	# run tests
	python -m pytest -vv --cov=app --cov-report term-missing tests/test_*.py


build:
	# build the package

deploy:
	# deploy the package