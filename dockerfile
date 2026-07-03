FROM python:3.13-slim

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

COPY ohayogozaimas.sh /config/ohayogozaimas.sh

WORKDIR /config

RUN chmod +x /config/ohayogozaimas.sh

ENTRYPOINT ["/config/ohayogozaimas.sh"]
