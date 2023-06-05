# Dockerfile
FROM python:3.9
ENV PYTHONUNBUFFERED 1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y netcat
COPY . /code/
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh
