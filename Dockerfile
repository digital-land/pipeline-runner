FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Install GDAL dependencies
RUN apt-get update -y && \
    apt-get install -y libgdal-dev gdal-bin && \
    rm -rf /var/lib/apt/lists/*

COPY . /src
WORKDIR /src

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements/requirements.txt

RUN make init && make update-dependencies

EXPOSE 5000

CMD ["uvicorn", "application.app:app", "--host", "0.0.0.0", "--port", "5000"]
