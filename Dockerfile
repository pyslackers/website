FROM pyslackers/python:3.6-alpine

RUN apk add --update --no-cache postgresql-dev

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN ./manage.py collectstatic
CMD ./manage.py migrate && gunicorn config.wsgi:application
