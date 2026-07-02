FROM python:3.13-slim

WORKDIR /config

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR /config/config

RUN python manage.py collectstatic --noinput

COPY ohayogozaimas.sh /ohayogozaimas.sh
RUN chmod +x /ohayogozaimas.sh

ENTRYPOINT ["/ohayogozaimas.sh"]
