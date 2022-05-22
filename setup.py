#!/usr/bin/env python

from setuptools import setup

setup(
    name="relay",
    version="1.0",
    description="Webhook relay",
    author="Tom Petr",
    author_email="trpetr@gmail.com",
    packages=["relay"],
    install_requires=["flask", "gunicorn", "prometheus-flask-exporter"],
)
