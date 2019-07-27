FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /conf
WORKDIR /conf
ADD ./service-requirements.txt /conf/
RUN apt-get update && \
    apt-get install -y vim && \
    pip install --upgrade pip && \
    pip install mysqlclient && \
    pip install djangorestframework django-filter && \
    pip install -r service-requirements.txt && \
    useradd -m -s /bin/bash -u 1000 wataru && \
    mkdir /var/log/uwsgi && \
    mkdir /app && \
    mkdir /app/project 
ADD ./service-uwsgi.ini /app/uwsgi.ini

WORKDIR /app/project



