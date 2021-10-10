FROM python:3.8-alpine

WORKDIR /app
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY main.py main.py

CMD [ "python3", "main.py"]