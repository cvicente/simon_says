import json
import logging

import falcon

from simon_says.control import Controller
from simon_says.db import DataStore
from simon_says.events import AlarmEvent, EventStore
from simon_says.log import configure_logging
from simon_says.sensors import Sensors, SensorState
from simon_says.version import __version__

logger = logging.getLogger(__name__)


class EventsResource:
    """ API resource for Events """

    def __init__(self, event_store: EventStore, sensors: Sensors, controller: Controller) -> None:

        self.event_store = event_store
        self.sensors = sensors
        self.controller = controller

    def _set_sensor_state(self, event: AlarmEvent) -> None:
        """ Set the sensor state depending on the event code """

        category = event.category
        if event.sensor and category == "Troubles":
            sensor = self.sensors.by_number(event.sensor)
            logger.info("Setting sensor %s (%s) state to 'open'", event.sensor, event.sensor_name)
            sensor.state = SensorState.OPEN
        else:
            logger.debug("_set_sensor_state: Ignoring event %s", event.uid)

    def on_get(self, req, resp, uid: str = None):
        """ Handle GET requests for events in the queue """

        if uid:
            logger.info("Getting event with uid %s", uid)

            try:
                e = self.event_store.get(uid=uid)
                resp.body = e.to_json()
            except KeyError:
                logger.error("uid %s not found", uid)
                raise falcon.HTTPNotFound()

        else:
            logger.info("Getting all events")
            resp.body = self.event_store.events_as_json()

        resp.content_type = "application/json"
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        """ Handle POST requests for event """

        data = req.media
        try:
            logger.info("Adding new event with uid %s", data["uid"])
            event = AlarmEvent(**data)
            self.event_store.add(event)
            self._set_sensor_state(event)
        except Exception as err:
            logger.error("Error creating AlarmEvent: %s", err)
            raise falcon.HTTPBadRequest()

        resp.status = falcon.HTTP_201
        resp.content_type = "application/json"
        resp.body = json.dumps({"result": "OK"})


class ControllerResource:
    """ API resource for commands and state """

    def __init__(self, sensors: Sensors, controller: Controller = None) -> None:
        self.sensors = sensors
        self.controller = controller

    def on_post(self, req, resp):
        """ Handle POST requests for commands """

        data = req.media
        if "action" not in data:
            logger.error("Missing required parameter: 'action'")
            raise falcon.HTTPBadRequest()

        action = data["action"]
        try:
            logger.info("Sending command %s", action)
            if action == "disarm":
                self.controller.disarm()
                self.sensors.clear_all()
            elif action == "arm_home":
                self.controller.arm_home()
            elif action == "arm_away":
                self.controller.arm_away()
            else:
                # Pass other less common actions
                self.controller.send_command(action)

        except Exception as err:
            logger.error("Error sending action to Alarm: %s", err)
            raise falcon.HTTPBadRequest()

        resp.status = falcon.HTTP_202
        resp.content_type = "application/json"
        resp.body = json.dumps({"result": "OK"})


class SensorsResource:
    """ Sensors resource class """

    def __init__(self, sensors: Sensors) -> None:
        self.sensors = sensors

    def on_get(self, req, resp, number: int = None):
        """ Handle GET requests for a given sensor number """

        if number:
            try:
                sensor = self.sensors.by_number(int(number))
                resp.body = sensor.to_json()
            except KeyError:
                logger.error("number %s not found", number)
                raise falcon.HTTPNotFound()
        else:
            logger.info("Getting all sensors")
            resp.body = self.sensors.all_as_json()

        resp.content_type = "application/json"
        resp.status = falcon.HTTP_200


class VersionResource:
    def on_get(self, req, resp):
        """ Handle GET requests for API version """

        resp.content_type = "application/json"
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({"version": __version__})


def create_app(controller: Controller = None, log_level: str = "INFO") -> falcon.API:
    """ Create a Falcon.API object """

    # Wire up the app handler with gunicorn's
    gunicorn_logger = logging.getLogger("gunicorn.error")
    configure_logging(log_level=log_level, handlers=gunicorn_logger.handlers)

    api = falcon.API()

    if not controller:
        controller = Controller()

    version_resource = VersionResource()
    api.add_route("/version", version_resource)

    sensors = Sensors()
    sensors_resource = SensorsResource(sensors=sensors)
    api.add_route("/sensors", sensors_resource)
    api.add_route("/sensors/{number}", sensors_resource)

    db = DataStore()
    events_resource = EventsResource(event_store=EventStore(db=db), sensors=sensors, controller=controller)
    api.add_route("/events", events_resource)
    api.add_route("/events/{uid}", events_resource)

    controller_resource = ControllerResource(sensors=sensors, controller=controller)
    api.add_route("/control", controller_resource)

    return api
