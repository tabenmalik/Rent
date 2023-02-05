FROM python:3.11

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

