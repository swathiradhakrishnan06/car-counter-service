install:
	# install packages
	pip install --upgrade pip && \
		pip install -r requirements.txt && \
			pip install python-multipart

format:
	# format code
	black **/*.py

lint:
	# run the linter
	pylint --disable=R,C **/*.py

test:
	# run tests
	python -m pytest -vv --cov=app/services --cov-report term-missing tests/test_*.py

build:
	# build the package
	docker build -t deploy-traffic-counter .

deploy:
	# deploy the package