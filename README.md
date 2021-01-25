# GE/Interlogix Simon XT API

Interact with a GE/Interlogix Simon XT using a REST API. 

The only usable remote interface to the Simon XT (other than cellular modules) is the PSTN, so we
use [Asterisk](https://www.asterisk.org/) and a SIP ATA to communicate with the unit.

This package includes:

* The WSGI server (app)
* A client library
* An event handler script to parse Asterisk's `alarmreceiver` events and submit them to the API

With this API, you can:

* Get a list of sensors, and their state (open/closed)
* Submit new events
* List events
* Get a single event using its UID
* Get the alarm's state (disarmed, armed_home, armed_away)
* Send the following commands:
    * arm_home
    * arm_away
    * disarm

Sample outputs:

```
# http localhost:8000/events
HTTP/1.1 200 OK
Connection: close
Date: Sun, 03 Jan 2021 21:24:23 GMT
Server: gunicorn/20.0.4
content-length: 274
content-type: application/json

[
    {
        "account": 1234,
        "checksum": 3,
        "code": 601,
        "code_description": "Manual trigger test report Zone",
        "extension": "100",
        "msg_type": 18,
        "partition": 0,
        "qualifier": 1,
        "status": null,
        "timestamp": 1609709046.0,
        "uid": "mpCeGa",
        "user": null,
        "zone": 0,
        "zone_name": null
    }
]

# http localhost:8000/sensors
HTTP/1.1 200 OK
Connection: close
Date: Mon, 18 Jan 2021 22:57:15 GMT
Server: gunicorn/20.0.4
content-length: 951
content-type: application/json

[
    {
        "name": "nothing",
        "number": 0,
        "state": "closed"
    },
    {
        "name": "front door",
        "number": 1,
        "state": "closed"
    },
]
```

## Persistence

This API uses [Redis](https://redis.io/) to store and persist events.

# Installation

## Server

The server can be run either as a Docker container, or directly on the host, once the library
is installed.

The Docker container includes an Asterisk instance. The easiest way to get up and running is cloning the repo and using
docker-compose. 

Before you run the container, copy the sample config.ini and edit it with your sensor information:

```buildoutcfg
cp config.ini.sample config.ini
EDITOR config.ini
...
```

You will also need to provide your own Asterisk configurations:

```buildoutcfg
cp /path-to-my-asterisk-configs ./asterisk_configs
```

A working `alarmreceiver.conf` file should be:

```buildoutcfg
[general]

timestampformat = %a %b %d, %Y @ %H:%M:%S %Z
eventcmd = python3 /app/bin/simon_event_handler
eventspooldir = /var/spool/asterisk/alarm_events
logindividualevents = yes
fdtimeout = 2000
sdtimeout = 40000
answait = 1250
loudness = 4096
```

And then:

```
docker-compose up -d
```


## Library
```
pip install simon_says
```

# Links

* [Interlogix Simon XT](https://www.interlogix.com/intrusion/product/simon-xt)
* [Asterisk Alarm receiver](https://www.voip-info.org/asterisk-cmd-alarmreceiver/)

# Author

Carlos Vicente