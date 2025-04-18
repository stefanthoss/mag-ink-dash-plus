FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium curl fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade poetry>=1.8

COPY poetry.lock pyproject.toml src /app/

RUN poetry install --only main --no-interaction

CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "--port", "5000", "main:app"]
