# Usage: docker build --no-cache --network=host --tag=threat_containment:v0.1 .

FROM python:3.6
WORKDIR /app
#COPY . /app
COPY /config /app/config
COPY /lab-manager /app/lab-manager
COPY /modules /app/modules


RUN pip3 install --trusted-host pypi.python.org -r lab-manager/requirements.txt

#RUN echo "Europe/Rome" > /etc/timezone
#RUN dpkg-reconfigure -f noninteractive tzdata

CMD [ "python", "-u", "/app/lab-manager/lab_manager.py" ]
#CMD [ "python", "-u", "/app/threat_containment.py" ]
