FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8 AS production

COPY . /src
WORKDIR /src
RUN pip install --user -U pip
RUN pip install --user --no-cache-dir -r requirements/requirements.txt

EXPOSE 3000

ENV PATH=/root/.local/bin:$PATH
ENV MODULE_NAME=application.app
ARG RELEASE_TAG
ENV RELEASE_TAG=${RELEASE_TAG}

FROM production AS dev
WORKDIR /src
RUN pip install --user --no-cache-dir -r requirements/dev-requirements.txt
RUN make init && make update-dependencies
