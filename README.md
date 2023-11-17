# Pipeline Runner API (temporary name)

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
- After cloning this repo, run the following command to download all the dependencies:
    ```
    make init
    ```

## Start Server
- To start the server run the following command:
    ```
    make server
    ```

## Adding new dependencies
- Project dependencies are managed via pip-tools
- to add a dependency, write it on a new line in ` /requirements/requirements.in ` or ` /requirements/dev-requirements.`
- to install the requirements from your requirements.in file run:
    ```
    make update-dependencies
    ```


## Testing
Testing is done using `pytest` with `playwrite` also being used for the acceptance tests.
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
