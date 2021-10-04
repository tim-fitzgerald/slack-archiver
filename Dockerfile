FROM python:3.9-slim-buster

ENV APP_HOME /slackarchiver
WORKDIR $APP_HOME

COPY . $APP_HOME

RUN python -m pip install -U pip
RUN python -m pip install -r requirements.txt

CMD ["python","slackarchiver/activity_archiver.py"]