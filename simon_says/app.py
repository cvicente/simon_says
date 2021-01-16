import json
import logging

import falcon

from simon_says.control import Controller
from simon_says.events import AlarmEvent, EventStore
from simon_says.sensors import Sensors, SensorState

logger = logging.getLogger(__name__)


class EventsResource:
    """ API resource for Events """

    def __init__(self, event_store: EventStore, sensors: Sensors) -> None:

        self.event_store = event_store
        self.sensors = sensors

    def _set_sensor_state(self, event: AlarmEvent) -> None:
        """ Set the sensor state depending on the event code """

        category = event.category
        if event.sensor and category == "Troubles":
            sensor = self.sensors.by_number(event.sensor)
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
                logger.error("uid %s not found")
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
        self.controller = controller or Controller()

    def on_get(self, req, resp):
        """ Handle GET requests for controller state """

        resp.body = json.dumps({"state": str(self.controller.state.name)})

        resp.content_type = "application/json"
        resp.status = falcon.HTTP_200

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


def create_app(controller: Controller = None) -> falcon.API:
    """ Create a Falcon.API object """

    api = falcon.API()

    sensors = Sensors()
    events_resource = EventsResource(event_store=EventStore(), sensors=sensors)
    api.add_route("/events", events_resource)
    api.add_route("/events/{uid}", events_resource)

    controller_resource = ControllerResource(sensors=sensors, controller=controller)
    api.add_route("/control", controller_resource)

    return api
