FROM ubuntu:20.04
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y python3-pip
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt
CMD python3 app.py