FROM nginx:1.17

RUN useradd -m -s /bin/bash -u 1000 wataru

RUN sed -i 's/user\ \ nginx\;/user\ \ wataru\;/g' /etc/nginx/nginx.conf

RUN apt-get update && apt-get install -y vim && \
    apt-get install -y curl && \
    apt-get install -y procps && \
    mkdir /var/log/nginx/site && \
    mkdir /var/log/nginx/service

# RUN /bin/cp -f /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
ADD ./uwsgi_params /etc/nginx/uwsgi_params
ADD ./vhost.conf /etc/nginx/conf.d/default.conf

WORKDIR /var/www
