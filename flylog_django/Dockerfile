# pull official base image
FROM python:3-alpine

# set work directory
WORKDIR /usr/src/flylog_django
# RUN mkdir /usr/src/flylog_django/static
# RUN touch /usr/src/flylog_django/static/test

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
# COPY . .
