FROM python:3.10-alpine

ENV PATH="/scripts:${PATH}"

# set working directory
WORKDIR /usr/src/app

# set environmrnt variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
COPY ./poetry.lock ./pyproject.toml ./
RUN pip install --upgrade pip
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install -n --no-ansi

# copy entrypoint.sh
COPY ./scripts ./scripts

RUN sed -i 's/\r$//g' /usr/src/app/scripts/entrypoint.sh
RUN chmod +x /scripts/*

COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]