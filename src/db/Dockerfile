FROM python:3.11-alpine

WORKDIR /workdir
COPY ./requirements.txt ./requirements.txt

RUN apk add --update gcc g++ python3-dev && \
    python3 -m pip install -r requirements.txt

COPY . .

CMD [ "python3", "./make_migrations.py", "-a", "5" ]
