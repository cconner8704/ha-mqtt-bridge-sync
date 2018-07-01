FROM python:3
MAINTAINER Chris Conner chrism.conner@gmail.com

#Install requests, flask and supervisor
RUN pip install requests
RUN pip install flask
RUN apt-get update && apt-get install -y supervisor

#Make log dir for supervisor
RUN mkdir -p /var/log/supervisor

#Copy supervisor conf and app
COPY ha-mqtt-bridge-sync-supervisord.conf /etc/supervisor/conf.d/ha-mqtt-bridge-sync-supervisord.conf
COPY app.py /app.py

#Environment variables
ENV PORT 5000
ENV OAUTH 123-123-123-123
ENV BRIDGEHOST bridge.example.com
ENV BRIDGEPORT 8080

#Expose ports
EXPOSE ${PORT}

CMD ["/bin/sleep 1000000"]
#CMD ["/usr/bin/supervisord"]
