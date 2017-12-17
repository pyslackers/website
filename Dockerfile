FROM pyslackers/python:3.6-alpine

RUN apk add --update --no-cache gcc g++ postgresql-dev

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app
COPY requirements /app/requirements
RUN pip install -r requirements/production.txt
COPY . .
RUN ./manage.py collectstatic
CMD ./manage.py migrate && gunicorn config.wsgi:application
