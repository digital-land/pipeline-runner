# Pipeline Runner API

This repo serves as a way to run a given resource through the pipeline in order to provide validation/information on the data.

## Prerequisites
- Python 3.6 or above
- Create a virtual environment using
    ```
    python3 -m venv --prompt . .venv --clear --upgrade-deps
    ```
  and activate it using
    ```
    source .venv/bin/activate
    ```

## Initialisation
- After cloning this repo, run the following command to set up the repo:
    ```
    make init
    ```

## Adding new dependencies
- Project dependencies are managed via pip-tools
- to add a dependency, write it on a new line in ` /requirements/requirements.in ` or ` /requirements/dev-requirements.in`
- to install the requirements run:
    ```
    make update-dependencies
    ```


## Start Server
- To start the server run the following command:
    ```
    make server
    ```


## Testing
Testing is done using `pytest`
- To run unit tests run:
    ```
    make test-unit
    ```
- To run integration tests run:
    ```
    make test-integration
    ```
- To run acceptance tests run:
    ```
    make test-acceptance
    ```

## Linting
We use [flake8](https://flake8.pycqa.org/en/latest/) for linting, combined with [black](https://black.readthedocs.io/en/stable/) for automatic code formatting
- To run the linting checks and code formatter run:
    ```
    make lint
    ```
