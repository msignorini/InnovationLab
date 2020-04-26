# Usage: docker build --no-cache --network=host --tag=threat_containment:v0.1 .

FROM python:3.6
WORKDIR /app
#COPY . /app
COPY /config /app/config
COPY /threat-containment /app/threat-containment
COPY /modules /app/modules


RUN pip3 install --trusted-host pypi.python.org -r threat-containment/requirements.txt

#RUN echo "Europe/Rome" > /etc/timezone
#RUN dpkg-reconfigure -f noninteractive tzdata

CMD [ "python", "-u", "/app/threat-containment/threat_containment.py" ]
