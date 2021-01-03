# GE/Interlogix Simon XT API

Interact with a GE/Interlogix Simon XT using a REST API. 

The only usable remote interface to the Simon XT (other than cellular modules) is the PSTN, so we
use [Asterisk](https://www.asterisk.org/) and a SIP ATA to communicate. 

This package includes:

* The WSGI server (app)
* A client library
* An event handler script to parse `alarmreceiver` events and submit them to the API

The REST API provides the following:

* Submit new events
* List events
* Getting a single event using its UID
* Sending the following commands:
    * arm_home
    * arm_away
    * disarm

Sample output:

```buildoutcfg
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
        "extension": "102",
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

```

## Persistence

The API does not persist event data, so reloading the server will clear the events queue.
This can be solved easily in the future by adding a Redis backend, or similar.

# Installation

## Server

The server can be run either as a Docker container, or directly on the host, once the library
is installed.

The Docker container includes an asterisk instance. The easiest way to get up and running is using
docker-compose. 

Before you run the container, copy the sample config.ini and edit it with your zones:

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