FROM python:3.13-slim

WORKDIR /config

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

COPY ohayogozaimas.sh config/ohayogozaimas.sh

WORKDIR /config

RUN chmod +x /ohayogozaimas.sh

ENTRYPOINT ["/ohayogozaimas.sh"]
