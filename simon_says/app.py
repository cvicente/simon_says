import json
import logging

import falcon

from simon_says.control import Controller
from simon_says.events import AlarmEvent, EventQueue

logger = logging.getLogger(__name__)


class EventsResource:
    """ API resource for Events """

    def __init__(self, event_queue: EventQueue) -> None:

        self.event_queue = event_queue

    def on_get(self, req, resp, uid: str = None):
        """ Handle GET requests for events in the queue """

        if uid:
            logger.info("Getting event with uid %s", uid)

            try:
                e = self.event_queue.get(uid=uid)
                resp.body = e.to_json()
            except KeyError:
                logger.error("uid %s not found")
                raise falcon.HTTPNotFound()

        else:
            logger.info("Getting all events")
            resp.body = self.event_queue.events_as_json

        resp.content_type = "application/json"
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        """ Handle POST requests for event """

        data = req.media
        try:
            logger.info("Adding new event with uid %s", data["uid"])
            event = AlarmEvent(**data)
            self.event_queue.add(event)
        except Exception as err:
            logger.error("Error creating AlarmEvent: %s", err)
            raise falcon.HTTPBadRequest()

        resp.status = falcon.HTTP_201
        resp.content_type = "application/json"
        resp.body = json.dumps({"result": "OK"})


class ControllerResource:
    """ API resource for commands """

    def __init__(self, controller: Controller = None) -> None:
        self.controller = controller or Controller()

    def on_post(self, req, resp):
        """ Handle POST requests for commands """

        data = req.media
        if "action" not in data:
            logger.error("Missing required parameter: 'action'")
            raise falcon.HTTPBadRequest()

        action = data["action"]
        try:
            logger.info("Sending command %s", action)
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

    events_resource = EventsResource(event_queue=EventQueue())
    api.add_route("/events", events_resource)
    api.add_route("/events/{uid}", events_resource)

    controller_resource = ControllerResource(controller=controller)
    api.add_route("/command", controller_resource)

    return api
