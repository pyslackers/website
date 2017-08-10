FROM pyslackers/python:3.6-alpine

RUN apk add --update --no-cache postgresql-dev

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE="config.settings.production" \
    GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --workers=4 --threads=4 --access-logfile - --log-level info --capture-output"

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
VOLUME /app/collected-static/
RUN ./manage.py collectstatic
CMD ./manage.py migrate && gunicorn config.wsgi:application
