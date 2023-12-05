FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10 AS production

COPY . /src
WORKDIR /src
RUN pip install --user -U pip
RUN pip install --user --no-cache-dir -r requirements/requirements.txt

EXPOSE 5000

ENV MODULE_NAME=application.app
ARG RELEASE_TAG
ENV RELEASE_TAG=${RELEASE_TAG}

FROM production AS dev
WORKDIR /src
RUN pip install --user --no-cache-dir -r requirements/dev-requirements.txt
RUN make init && make update-dependencies
