
# deduce the repository
ifeq ($(REPOSITORY),)
REPOSITORY=$(shell basename -s .git `git config --get remote.origin.url`)
endif

ifeq ($(ENVIRONMENT),)
ENVIRONMENT=production
endif

ifeq ($(SOURCE_URL),)
SOURCE_URL=https://raw.githubusercontent.com/digital-land/
endif

ifeq ($(CONFIG_URL),)
CONFIG_URL=https://raw.githubusercontent.com/digital-land/config/main/
endif

ifeq ($(CACHE_DIR),)
CACHE_DIR=var/cache/
endif

# =============================
# Utils
# =============================

server::
	python -m uvicorn application.app:app --reload --port=8082

# build docker image

# =============================
# Dependencies
# =============================

init::
	python -m pip install pip-tools
	make piptool-compile
	make dependencies
	make pre-commit-install

piptool-compile::
	python -m piptools compile --output-file=requirements/requirements.txt requirements/requirements.in
	python -m piptools compile --output-file=requirements/dev-requirements.txt requirements/dev-requirements.in

dependencies::
	pip-sync requirements/requirements.txt  requirements/dev-requirements.txt

pre-commit-install::
	pre-commit install


# update makerules from source
makerules::
	curl -qfsL '$(SOURCE_URL)/makerules/main/makerules.mk' > makerules/makerules.mk

ifeq (,$(wildcard ./makerules/specification.mk))
# update local copies of specification files
specification::
	@mkdir -p specification/
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/attribution.csv' > specification/attribution.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/licence.csv' > specification/licence.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/typology.csv' > specification/typology.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/theme.csv' > specification/theme.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/collection.csv' > specification/collection.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/dataset.csv' > specification/dataset.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/dataset-field.csv' > specification/dataset-field.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/field.csv' > specification/field.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/datatype.csv' > specification/datatype.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/prefix.csv' > specification/prefix.csv
	# deprecated ..
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/pipeline.csv' > specification/pipeline.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/dataset-schema.csv' > specification/dataset-schema.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/schema.csv' > specification/schema.csv
	curl -qfsL '$(SOURCE_URL)/specification/main/specification/schema-field.csv' > specification/schema-field.csv


init::	specification
endif

# local copy of organsiation datapackage
$(CACHE_DIR)organisation.csv:
	@mkdir -p $(CACHE_DIR)
	curl -qfs "https://raw.githubusercontent.com/digital-land/organisation-dataset/main/collection/organisation.csv" > $(CACHE_DIR)organisation.csv


# =============================
# Linting
# =============================

lint:
	make black ./application
	python3 -m flake8 ./application
	make jslint

black-check:
	black --check .

black:
	python3 -m black .

jslint::
	npx eslint --ext .html,.js ./

jslint-fix::
	npx eslint --ext .html,.js ./ --fix

# =============================
# Testing
# =============================

test-acceptance:
	python -m playwright install chromium
	python -m pytest --md-report --md-report-color=never -p no:warnings tests/acceptance

test: test-unit test-integration

test-unit:
	python -m pytest --md-report --md-report-color=never --md-report-output=unit-tests.md tests/unit

test-integration:
	python -m pytest --md-report --md-report-color=never --md-report-output=integration-tests.md tests/integration

test-integration-docker:
	docker-compose run web python -m pytest tests/integration --junitxml=.junitxml/integration.xml $(PYTEST_RUNTIME_ARGS)

# Security
