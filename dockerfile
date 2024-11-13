FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry


COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-root

COPY . /app

RUN sqlite3 /app/app/db/database.db ""

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
