# Stage 1: Build stage
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10 AS builder

# Install GDAL dependencies
RUN apt-get update -y && \
    apt-get install -y libgdal-dev gdal-bin && \
    rm -rf /var/lib/apt/lists/*

COPY . /src
WORKDIR /src

RUN pip install --user -U pip
RUN pip install --user --no-cache-dir -r requirements/requirements.txt
RUN make init && make update-dependencies

# Stage 2: Final stage
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10


COPY --from=builder /src /app

#Try copying only the required files
# Expose the application port
EXPOSE 5000

# Command to run the application
CMD ["uvicorn", "application.app:app", "--host", "0.0.0.0", "--port", "5000"]
