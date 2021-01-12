FROM python:3.8.1-alpine
WORKDIR /app

ENV PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
EXPOSE ${PORT}

RUN apk add --no-cache tzdata gcc g++ make postgresql-dev build-base git && \
    cp /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" >> /etc/timezone && \
    apk del tzdata

RUN apk add --no-cache libffi-dev git

COPY requirements requirements
RUN pip install -r requirements/development.txt

COPY . .

CMD gunicorn \
	pyslackersweb:app_factory \
	--bind=0.0.0.0:${PORT} \
	--worker-class=aiohttp.GunicornUVLoopWebWorker
