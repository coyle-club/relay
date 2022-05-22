FROM docker.io/python:3.10.4-slim

COPY wh_relay /app/wh_relay

COPY setup.py /app/setup.py

RUN pip install -e /app

ENTRYPOINT ["/usr/local/bin/gunicorn"]
CMD ["wh_relay:app"]


