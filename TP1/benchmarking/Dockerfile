FROM python:3.8-slim

WORKDIR /app
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY main.py main.py
COPY analytics.py analytics.py
COPY benchmark.py benchmark.py

CMD [ "python3", "main.py"]