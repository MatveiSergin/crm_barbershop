FROM ubuntu:latest

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    curl apt-utils apt-transport-https gcc build-essential \
    python3 python3-pip python3-venv apache2 libapache2-mod-wsgi-py3 \
    && a2enmod wsgi && apachectl -M
RUN apt-get install -y libpq-dev libonig-dev

RUN apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen

RUN apt-get install gettext nano vim -y

ENV PYTHONUNBUFFERED 1

RUN apt-get install -y python3

RUN python3 -m venv /venv

ENV PATH="/venv/bin:$PATH"
RUN pip3 install --upgrade pip
RUN pip3 install pyodbc

RUN echo "deb http://archive.ubuntu.com/ubuntu focal-backports main universe" >> /etc/apt/sources.list

RUN echo "deb http://archive.ubuntu.com/ubuntu focal main restricted universe multiverse" >> /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu focal-updates main restricted universe multiverse" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y xvfb
COPY ./requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r ./requirements.txt

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN echo   "deb http://archive.ubuntu.com/ubuntu focal-backports main universe multiverse" >> /etc/apt/sources.list
RUN apt-get update
RUN a2enmod headers && a2enmod wsgi

RUN apachectl -M | grep headers
RUN apachectl -M | grep wsgi

RUN chown -R www-data:www-data /venv

EXPOSE 80

CMD ["apache2ctl", "-D", "FOREGROUND"]
