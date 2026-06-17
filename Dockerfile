FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY requirements ./requirements

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY src ./src
COPY scripts ./scripts
COPY database ./database
COPY main.py ./main.py

RUN chmod +x /app/scripts/docker_start.sh /app/scripts/start_auth_service.sh

EXPOSE 8004

CMD ["./scripts/docker_start.sh"]
