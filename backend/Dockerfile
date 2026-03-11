FROM python:3.12-slim AS builder

ENV POETRY_VERSION=2.3.2
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --upgrade pip --default-timeout=100 \
 && pip install poetry==${POETRY_VERSION} --default-timeout=100 \
 && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --no-interaction --no-ansi

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
