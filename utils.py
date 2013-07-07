import sys, os, time
from threading import Thread

sys.path.insert(0, os.environ['PSMOVEAPI_BUILD_DIR'])
import psmove


class Controller(object):
    _active = False
    _keep_alive_thread = None

    controller = None

    color_red = 0
    color_green = 0
    color_blue = 0

    ax = 0
    ay = 0
    az = 0
    gx = 0
    gy = 0
    gz = 0
    btn_triangle = False
    btn_circle = False
    btn_cross = False
    btn_square = False
    btn_select = False
    btn_start = False
    btn_move = False
    btn_t = False
    btn_ps = False
    battery = 0

    rumble = 0

    def __init__(self, controller):
        self._active = True
        self.controller = controller

        self._keep_alive_thread = Thread(target=self._keep_alive_thread_loop)
        self._keep_alive_thread.daemon = True
        self._keep_alive_thread.start()

    def terminate(self):
        self._active = False
        self._keep_alive_thread.join()

    def _keep_alive_thread_loop(self):
        while(self._active):
            self.controller.set_leds(self.color_red, self.color_green, self.color_blue)
            self.controller.update_leds()
            time.sleep(1)

    def update_state(self):
        result = self.controller.poll()

        if result:
            buttons = self.controller.get_buttons()
            button_events_on, button_events_off = self.controller.get_button_events()

            self.btn_triangle = bool(buttons & psmove.Btn_TRIANGLE)
            self.btn_circle = bool(buttons & psmove.Btn_CIRCLE)
            self.btn_cross = bool(buttons & psmove.Btn_CROSS)
            self.btn_square = bool(buttons & psmove.Btn_SQUARE)
            self.btn_select = bool(buttons & psmove.Btn_SELECT)
            self.btn_start = bool(buttons & psmove.Btn_START)
            self.btn_move = bool(buttons & psmove.Btn_MOVE)
            self.btn_t = bool(buttons & psmove.Btn_T)
            self.btn_ps = bool(buttons & psmove.Btn_PS)
            self.battery = self.controller.get_battery()

            self.ax, self.ay, self.az = self.controller.get_accelerometer_frame(psmove.Frame_SecondHalf)
            self.gx, self.gy, self.gz = self.controller.get_gyroscope_frame(psmove.Frame_SecondHalf)

    def state_as_dict(self, update_first=True):
        if update_first:
            self.update_state()

        state_dict = {
            'ax': self.ax,
            'ay': self.ay,
            'az': self.az,
            'gx': self.gx,
            'gy': self.gy,
            'gz': self.gz,
            'btn_triangle': self.btn_triangle,
            'btn_circle': self.btn_circle,
            'btn_cross': self.btn_cross,
            'btn_square': self.btn_square,
            'btn_select': self.btn_select,
            'btn_start': self.btn_start,
            'btn_move': self.btn_move,
            'btn_t': self.btn_t,
            'btn_ps': self.btn_ps,
            'color_red': self.color_red,
            'color_green': self.color_green,
            'color_blue': self.color_blue,
            'rumble': self.rumble,
        }

        return state_dict

    def set_color(self, red=None, green=None, blue=None):
        if red is not None:
            self.color_red = red

        if green is not None:
            self.color_green = green

        if blue is not None:
            self.color_blue = blue

        self.controller.set_leds(self.color_red, self.color_green, self.color_blue)
        self.controller.update_leds()

    def set_rumble(self, rumble):
        self.rumble = rumble
        self.controller.set_rumble(rumble)


def get_controllers():
    controllers = [psmove.PSMove(x) for x in range(psmove.count_connected())]
    return [Controller(c) for c in controllers if c.connection_type == psmove.Conn_Bluetooth]
