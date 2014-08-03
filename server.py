"""PS Move Restful Server

Usage:
  server.py [--battery-saver]

Options:
  --battery_saver  If set, only allows a few seconds without a GET request before shutting off a controllers LEDs and rumble

"""
from docopt import docopt
import datetime
import time
from threading import Thread
from flask import Flask
from flask.ext.restful import reqparse, abort, Api, Resource

try:
    from settings import CONTROLLER_SERIALS
except ImportError:
    CONTROLLER_SERIALS = {}
    

from utils import get_controllers



app = Flask(__name__)
api = Api(app)



controllers = get_controllers()


def color_type(val):
    val = int(val)

    if val < 0 or val > 255:
        raise ValueError("Colors must be between 0 and 255")

    return val


def rumble_type(val):
    val = int(val)

    if val < 0 or val > 255:
        raise ValueError("Rumble must be between 0 and 255")

    return val


parser = reqparse.RequestParser()
parser.add_argument('red', type=color_type)
parser.add_argument('green', type=color_type)
parser.add_argument('blue', type=color_type)
parser.add_argument('rumble', type=rumble_type)


def get_controller_by_id(controller_id):
    if CONTROLLER_SERIALS:
        serial = CONTROLLER_SERIALS.get(controller_id)

        if not serial:
            return None

        for controller in controllers:
            if controller.controller.get_serial() == serial:
                return controller

        return None
        
    try:
        return controllers[controller_id]
    except IndexError:
        return None


class ControllerListResource(Resource):
    def get(self):
        return [controller.state_as_dict() for controller in controllers]


class ControllerResource(Resource):
    def get(self, controller_id):
        controller = get_controller_by_id(controller_id)

        if controller is None:
            abort(404, message="Controller {} doesn't exist".format(controller_id))

        controller.last_accessed = datetime.datetime.now()

        return controller.state_as_dict()

    def put(self, controller_id):
        controller = get_controller_by_id(controller_id)
        
        if controller is None:
            abort(404, message="Controller {} doesn't exist".format(controller_id))

        args = parser.parse_args()
        
        red = args['red']
        green = args['green']
        blue = args['blue']
        
        controller.set_color(red, green, blue)

        rumble = args['rumble']

        if rumble is not None:
            controller.set_rumble(rumble)

        return 'Updated', 201


api.add_resource(ControllerListResource, '/controllers/')
api.add_resource(ControllerResource, '/controllers/<int:controller_id>/')


def battery_saver_factory(seconds):
    def battery_saver():
        while(True):
            for controller in controllers:
                if controller.red or controller.green or controller.blue or controller.rumble:
                    time_since_last_accessed = datetime.datetime.now() - controller.last_accessed

                    if (time_since_last_accessed.days * 86400 + time_since_last_accessed.seconds > seconds):
                        controller.set_color(0, 0, 0)
                        controller.set_rumble(0)

            time.sleep(0.5)

    return battery_saver


def main():
    arguments = docopt(__doc__, version='PS Move Restful Server')
    battery_saver_mode = arguments['--battery-saver']

    for controller in controllers:
        controller.last_accessed = datetime.datetime.now()

    if battery_saver_mode:
        battery_saver_thread = Thread(target=battery_saver_factory(3))
        battery_saver_thread.daemon = True
        battery_saver_thread.start()

    app.run(debug=False, use_reloader=False)

    for controller in controllers:
        controller.terminate()


if __name__ == '__main__':
    main()

