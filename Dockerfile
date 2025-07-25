FROM python:3.12-alpine
WORKDIR /app

ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
EXPOSE ${PORT}

RUN apk add --no-cache tzdata gcc g++ make postgresql-dev build-base git && \
    cp /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" >> /etc/timezone && \
    apk del tzdata

# Copy just the dependency specification first for better caching
COPY pyproject.toml ./
RUN pip install -U pip && \
    pip install .

COPY . .

CMD gunicorn \
	pyslackersweb:app_factory \
	--bind=0.0.0.0:${PORT} \
	--worker-class=aiohttp.GunicornUVLoopWebWorker
