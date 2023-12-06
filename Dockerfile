FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10 AS production
COPY . /src
WORKDIR /src

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements/requirements.txt


RUN make init && make update-dependencies

EXPOSE 5000

CMD ["uvicorn", "application.app:app", "--host", "127.0.0.1", "--port", "5000"]
