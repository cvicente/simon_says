# GE/Interlogix Simon XT API

Interact with a GE/Interlogix Simon XT using a REST API. 

The only usable remote interface to the Simon XT is the PSTN interface, so we
use Asterisk and SIP ATA to communicate. 

This package includes:

* The WSGI server (app)
* A client library
* An event handler script to parse alarmreceiver events and submit them to the API

The REST API provides the following:

* Submit new events
* List events
* Getting a single event using its UID
* Sending the following commands:
    * arm_home
    * arm_away
    * disarm

## Persistence

The API does not persist event data, so reloading the server will clear the events queue.
This can be solved easily in the future by adding a Redis backend, or similar.

# Installation

## Server

The server can be run either as a Docker container, or directly on the host, once the library
is installed.

For Docker, you can use docker-compose:

```
docker-compose up -d
```

## Library
```
pip install simon_says
```

# Author

Carlos Vicente