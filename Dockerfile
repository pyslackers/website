FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1 \
    PY_ENV development

WORKDIR /app

ADD requirements.txt /app/

RUN apk --no-cache add --virtual build-dependencies build-base \
  && apk --no-cache add postgresql-dev \
  && pip install -r requirements.txt \
  && apk del build-dependencies

ADD . /app/

EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
