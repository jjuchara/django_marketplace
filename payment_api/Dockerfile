FROM python:3.10-alpine

# set working directory
WORKDIR /home/api

# set environmrnt variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /home/api/requirements.txt

COPY . .



