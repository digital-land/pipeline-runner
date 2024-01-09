# Stage 1: Build stage
FROM python:3.10 AS builder

# Install GDAL dependencies
RUN apt-get update -y && \
    apt-get install -y libgdal-dev gdal-bin && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: Final stage
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY . /src
WORKDIR /src
# Run make commands to initialize and update dependencies
RUN make init && make update-dependencies

# Expose the application port
EXPOSE 5000

# Command to run the application
CMD ["uvicorn", "application.app:app", "--host", "0.0.0.0", "--port", "5000"]
