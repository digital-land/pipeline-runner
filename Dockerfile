# Stage 1: Build stage
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10 AS builder

COPY . /src
WORKDIR /src

RUN make init && make update-dependencies

# Stage 2: Final stage
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY --from=builder /src/application /app/application
COPY --from=builder /src/configs /app/configs
COPY --from=builder /src/tests /app/tests
COPY --from=builder /src/requirements /app/requirements
COPY --from=builder /src/specification /app/specification
COPY --from=builder /src/var /app/var

RUN pip install --no-cache-dir -r /app/requirements/requirements.txt

# Expose the application port
EXPOSE 5000

# Command to run the application
CMD ["uvicorn", "application.app:app", "--host", "0.0.0.0", "--port", "5000"]
