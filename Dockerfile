FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md /app/
RUN pip install --no-cache-dir -e .[dev]

COPY dataset_qa /app/dataset_qa
COPY configs /app/configs
COPY tests /app/tests

ENTRYPOINT ["python", "-m", "dataset_qa"]
