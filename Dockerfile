FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[dev]"

CMD ["python", "scripts/check_artifact.py"]
