FROM python:3.7.3-alpine
WORKDIR /app

ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements requirements

RUN apk add --no-cache tzdata gcc g++ make && \
    cp /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" >> /etc/timezone && \
    apk del tzdata

RUN pip install -r requirements/development.txt

COPY . .

CMD gunicorn pyslackersweb:app_factory --bind=0.0.0.0:${PORT} --worker-class=aiohttp.GunicornWebWorker
