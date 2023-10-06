FROM python:3.8-slim as builder
# create working directory in docker
WORKDIR /usr/src/app

# use appstream repository
#RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Linux-*
#RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-Linux-*

# redhat/centos
#RUN yum update -y
#RUN yum install -y mariadb-devel gcc python38-devel
#RUN pip3 install --upgrade pip

# python-slim (debian)
RUN apt-get update
# install gcc
RUN apt-get install -y build-essential
RUN apt-get install -y manpages-dev
# install mysql connector utility
RUN apt-get install -y libmariadb-dev
RUN pip3 install --upgrade pip

# copy project
COPY . .
# install dependencies
RUN pip3 install -r ./backend/requirements.txt

RUN mkdir ./backend/logs

# copy from builder
FROM python:3.8-slim

WORKDIR /home/stock

# python-slim (debian)
RUN apt-get update
# install gcc
RUN apt-get install -y build-essential
RUN apt-get install -y manpages-dev
# install mysql connector utility
RUN apt-get install -y libmariadb-dev
#RUN pip3 install --upgrade pip

RUN apt-get install -y vim

COPY --from=builder /usr/src/app .

COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages


# setting envirionment
ENV DJANGO_DATABASE mysql-docker
#ENV DJANGO_DATABASE mysql-local