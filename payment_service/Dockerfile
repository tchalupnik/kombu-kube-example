FROM python:3.8

ENV PYTHONPATH /home/worker
ENV PYTHONUNBUFFERED=1

WORKDIR /home/worker

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY src src

ENTRYPOINT python src/worker.py
