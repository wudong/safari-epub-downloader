from python:3

MAINTAINER wudong.liu@gmail.com

COPY . /app
WORKDIR /app

ENV PYTHONPATH=/app

RUN pip install pipenv

RUN pipenv install --system --deploy

CMD ["python", "web/api.py"]
