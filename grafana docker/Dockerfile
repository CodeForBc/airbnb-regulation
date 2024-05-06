FROM mysql/mysql-server:5.7

ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
ENV MYSQL_DATABASE=airbnbProjectDB

COPY ./init.sql /docker-entrypoint-initdb.d/