from flask import Flask
from flask.ext.restful import reqparse, abort, Api, Resource

from utils import get_controllers



app = Flask(__name__)
api = Api(app)


def color_type(val):
    val = int(val)

    if val < 0 or val > 255:
        raise ValueError("Colors must be between 0 and 255")

    return val


def rumble_type(val):
    val = int(val)

    if val < 0 or val > 100:
        raise ValueError("Rumble must be between 0 and 100")

    return val


parser = reqparse.RequestParser()
parser.add_argument('color_red', type=color_type)
parser.add_argument('color_green', type=color_type)
parser.add_argument('color_blue', type=color_type)
parser.add_argument('rumble', type=rumble_type)


def get_controller_by_id(controller_id):
    try:
        return controllers[controller_id]
    except IndexError:
        abort(404, message="Controller {} doesn't exist".format(controller_id))


class ControllerListResource(Resource):
    def get(self):
        return [controller.state_as_dict() for controller in controllers]


class ControllerResource(Resource):
    def get(self, controller_id):
        controller = get_controller_by_id(controller_id)

        return controller.state_as_dict()

    def put(self, controller_id):
        controller = get_controller_by_id(controller_id)

        args = parser.parse_args()
        
        red = args['color_red']
        green = args['color_green']
        blue = args['color_blue']
        
        controller.set_color(red, green, blue)

        rumble = args['rumble']

        if rumble is not None:
            controller.set_rumble(rumble)

        return 'Updated', 201


api.add_resource(ControllerListResource, '/controllers')
api.add_resource(ControllerResource, '/controllers/<int:controller_id>')


if __name__ == '__main__':
    controllers = get_controllers()

    app.run(debug=True, use_reloader=False)

    for controller in controllers:
        controller.terminate()
