from flask import Flask, request, jsonify
import click
import sqlite3
from time import time
import json
import os
from prometheus_flask_exporter import PrometheusMetrics

DB_FILENAME = os.environ.get("DB_FILENAME", "/var/lib/relay/relay.db")

with sqlite3.connect(DB_FILENAME) as conn:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS requests (timestamp integer, source text, remote_addr text, method text, headers json, body text)"
    )
    conn.commit()

app = Flask("relay")
metrics = PrometheusMetrics(app)


@app.route("/")
def sources():
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT source, MIN(rowid), MAX(rowid), MAX(timestamp) FROM requests GROUP BY source ORDER BY source ASC"
        )
        return jsonify(
            [
                dict(
                    source=row[0],
                    min_offset=row[1],
                    max_offset=row[2],
                    timestamp=row[3],
                )
                for row in cur.fetchall()
            ]
        )


@app.route(
    "/webhook/<source>",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
@metrics.counter(
    "relay_webhook_counter",
    "Webhook relay request counter",
    labels={
        "source": lambda: request.view_args["source"],
        "method": lambda: request.method,
    },
)
def receive_webhook(source):
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?)",
            (
                int(time() * 1000),
                source,
                request.remote_addr,
                request.method,
                json.dumps(dict(request.headers)),
                request.get_data().decode("utf-8"),
            ),
        )
        conn.commit()
    return "OK"


@app.route("/read/<source>")
def read(source):
    limit = min(int(request.args.get("limit", 10)), 100)
    offset = int(request.args.get("offset", 0))
    with sqlite3.connect(DB_FILENAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT rowid, timestamp, source, remote_addr, method, headers, body FROM requests WHERE source = ? AND rowid > ? LIMIT ?",
            (source, offset, limit),
        )
        return jsonify(
            [
                dict(
                    offset=row[0],
                    timestamp=row[1],
                    source=row[2],
                    remote_addr=row[3],
                    method=row[4],
                    headers=json.loads(row[5]),
                    body=row[6],
                )
                for row in cur.fetchall()
            ]
        )
