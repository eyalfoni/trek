FROM python:3.7-alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
WORKDIR /trek
ENV FLASK_APP trek.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_DEBUG 1
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . ./trek
ENTRYPOINT [".docker/docker-entrypoint.sh"]