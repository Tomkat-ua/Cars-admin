FROM bitnami/python:3.9-debian-12

ENV TZ=Europe/Kiev

WORKDIR /app

RUN apt-get update  
RUN apt-get install  libfbclient2 -y --no-install-recommends
COPY templates/*    /app/templates/
COPY requirements.txt /app/
COPY admin.py /app/
COPY fbextract.py /app/
RUN pip install -r requirements.txt

CMD [ "python3", "admin.py" ]


