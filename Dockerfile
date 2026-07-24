FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# curl is only needed for the docker-compose healthcheck (US-18)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY mvp/src ./mvp/src

RUN pip install --upgrade pip && pip install -e .

EXPOSE 8000

CMD ["uvicorn", "open_housing_mvp.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
