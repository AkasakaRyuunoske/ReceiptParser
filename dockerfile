FROM python:3.13-slim

WORKDIR /config

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR /config/config

RUN python manage.py collectstatic --noinput

CMD gunicorn --bind 0.0.0.0:8000 config.wsgi:application