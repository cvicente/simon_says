FROM debian:buster-slim

RUN apt-get update -y && apt-get install -y \
    asterisk \
    net-tools \
    procps \
    python3-pip \
    python3-dev \
    supervisor

RUN mkdir /var/spool/asterisk/alarm_events && \
    mkdir /var/spool/asterisk/alarm_events_processed && \
    chown asterisk:asterisk /var/spool/asterisk/alarm_events*

COPY ./ /app
WORKDIR /app

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -e .

CMD ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]
