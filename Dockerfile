FROM docker.io/python:3.10.4-slim

COPY relay /app/relay

COPY setup.py /app/setup.py

RUN pip install -e /app

ENTRYPOINT ["/usr/local/bin/gunicorn"]
CMD ["--access-logfile", "-", "relay:app"]


