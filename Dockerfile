FROM python:3.6-alpine

RUN apk add --update --no-cache \
    g++ gcc postgresql-dev && \
    pip install dumb-init

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE="config.settings.production" \
    GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=4 --threads=4 --access-logfile - --log-level info --capture-output"

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
VOLUME /app/collected-static/
RUN ./manage.py collectstatic
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ./manage.py migrate && gunicorn config.wsgi:application