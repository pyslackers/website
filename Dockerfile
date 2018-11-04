# Front End Build
FROM node:9.6-alpine as node_builder

WORKDIR /app
COPY client client
COPY ["package.json", "yarn.lock", "/app/"]
RUN yarn install
RUN yarn run build:prod

# Python Goodness
FROM python:3.6.7-alpine

RUN apk add --update --no-cache gcc g++ postgresql-dev

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app
COPY requirements /app/requirements
RUN pip install -r requirements/production.txt
COPY . .
RUN mkdir -p /app/static/dist/
COPY --from=node_builder /app/app/static/dist /app/app/static/dist
RUN ./manage.py collectstatic
VOLUME /app/collected-static

CMD gunicorn -c config/gunicorn.py config.wsgi:application
