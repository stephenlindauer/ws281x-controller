#!/usr/bin/env python3

# How to Start/Stop service:
# sudo systemctl stop lights && sudo systemctl start lights
# sudo systemctl stop lights

try:
    from rpi_ws281x import Color
except Exception:
    from rpi_stub import Color
from led_system import LEDSystem
from programs.strobe import StrobeProgram
from programs.heartbeat import HeartbeatProgram
from programs.tail import TailProgram
from programs.candycane import CandyCaneProgram
from programs.pattern import PatternProgram
from programs.gradient import GradientProgram
import threading
from wsserver import WebSocketServer
from httpserver import HTTPServerWrapper
from named_colors import NamedColor
import json

# How many LEDs in total are in the setup
# led_count = 277
led_count = 800

componentConfig = {
    "components": [
        {
            "label": "root",
            "light_begin": "infer",
            "length": led_count,
            "components": [
                {
                    "label": "test_leds",
                    "light_begin": 0,
                    "length": 4
                },
                {
                    "label": "bridge1",
                    "disabled": True,
                    "light_begin": 4,
                    "length": 23
                },
                {
                    "label": "bottom_row",
                    "light_begin": 27,
                    "length": 250,
                    "components": [
                        {
                            "label": "strip1",
                            "light_begin": 27,
                            "length": 100,
                        },
                        {
                            "label": "strip2",
                            "light_begin": 127,
                            "length": 40,
                        },
                        {
                            "label": "strip3",
                            "light_begin": 167,
                            "length": 110,
                        },
                    ]
                },
                {
                    "label": "top_row",
                    "light_begin": 277,
                    "length": 523,
                    "components": [
                        {
                            "label": "peak_right",
                            "light_begin": 277,
                            "length": 172,
                            "components": [
                                {
                                    "label": "peak_right_r",
                                    "light_begin": 277,
                                    "length": 100,
                                },
                                {
                                    "label": "peak_right_l",
                                    "light_begin": 377,
                                    "length": 72,
                                },
                            ]
                        },
                        {
                            "label": "peak_left",
                            "light_begin": 531,  # TODO: Verify
                            "length": 170,
                            "components": [
                                {
                                    "label": "peak_left_r",
                                    "light_begin": 531,
                                    "length": 100,
                                },
                                {
                                    "label": "peak_left_l",
                                    "light_begin": 631,
                                    "length": 70,
                                },
                            ]
                        },
                    ]
                },
                {
                    "label": "bridge2",
                    "disabled": True,
                    "light_begin": 449,
                    "length": 82
                },
                # {
                #     "label": "section2",
                #     "light_begin": 77,
                #     "length": 150,
                # },
                # {
                #     "label": "section3",
                #     "light_begin": 200,
                #     "length": 150
                # },
                # {
                #     "label": "section4",
                #     "light_begin": 350,
                #     "length": 150
                # },
                # {
                #     "label": "section5",
                #     "light_begin": 500,
                #     "length": 150
                # },
                # {
                #     "label": "section6",
                #     "light_begin": 650,
                #     "length": 150
                # },
                # {
                #     "label": "section7",
                #     "light_begin": 800,
                #     "length": 200
                # },
            ]
        },
    ]
}

websocket_server = None


def preset1(system):
    system.getComponentByName("root").addProgram(
        TailProgram(
            length=10,
            rgb=[0, 0, 255],
            program_range=range(0, 400),
            speed=40),
        50)
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=10,
            gap_length=33),
        10)
    system.getComponentByName("section1").addProgram(
        StrobeProgram(),
        10)
    wreath = system.getComponentByName("section2")
    wreath.addProgram(
        CandyCaneProgram(
            stripe_length=21,
            gap_length=4,
            stripe_rgb=[0, 200, 0],
            gap_rgb=[255, 255, 50]),
        12)
    wreath.addProgram(
        CandyCaneProgram(
            stripe_length=2,
            offset=10,
            gap_length=23,
            stripe_rgb=[255, 255, 50],
            gap_rgb=None),
        13)
    system.getComponentByName("section3").addProgram(
        PatternProgram(
            colors=[(255, 0, 0), (255, 255, 255), (0, 0, 255),
                    (255, 0, 0), (0, 0, 0), (0, 0, 255)],
            multiplier=1,
            speed=1),
        15)
    system.getComponentByName("section4").addProgram(
        CandyCaneProgram(
            stripe_length=4,
            gap_length=7,
            speed=-20,
            stripe_rgb=(0, 255, 255),
            gap_rgb=(255, 0, 255)),
        15)
    system.getComponentByName("section5").addProgram(
        GradientProgram(speed=-10, length=25),
        20)
    system.getComponentByName("section6").addProgram(
        PatternProgram(
            colors=[(108, 47, 0), (158, 104, 42), (241, 185, 48),
                    (181, 71, 48), (138, 151, 72)],
            multiplier=6,
            speed=0.2),
        15)


def presetBlueWhiteShort(system):
    system.getComponentByName("top_row").addProgram(
        CandyCaneProgram(
            stripe_length=2,
            gap_length=2,
            stripe_rgb=[0, 0, 255]))
    system.getComponentByName("bottom_row").addProgram(
        CandyCaneProgram(
            stripe_length=2,
            speed=-10,
            gap_length=2,
            stripe_rgb=[0, 0, 255]))


def presetBlueWhiteLong(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=2,
            gap_length=9,
            stripe_rgb=[0, 0, 255]))


def presetRedGreen(system):
    system.getComponentByName("bottom_row").addProgram(
        CandyCaneProgram(
            stripe_length=20,
            gap_length=20,
            stripe_rgb=[0, 255, 0],
            gap_rgb=[255, 0, 0]))
    system.getComponentByName("top_row").addProgram(
        CandyCaneProgram(
            stripe_length=20,
            gap_length=20,
            speed=-10,
            stripe_rgb=[0, 255, 0],
            gap_rgb=[255, 0, 0]))


def presetThanksgiving(system):
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[(108, 47, 0), (158, 104, 42), (241, 185, 48),
                    (181, 71, 48), (138, 151, 72)],
            multiplier=1,
            speed=0.2),
        15)


def presetBlueOffShort(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=6,
            gap_length=10,
            gap_rgb=[0, 0, 0],
            stripe_rgb=[0, 0, 255]))


def presetBlueWhiteSingles(system):
    blue = (0, 0, 255)
    off = (0, 0, 0)
    white = (255, 255, 255)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[white, off, off, off, blue, off, off, off, off, off, off],
            multiplier=1,
            speed=1),
        15)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[white, None, None, None, None, None],
            multiplier=1,
            speed=-1),
        16)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[blue, None, None, None, None, None, None],
            multiplier=1,
            speed=2),
        16)


def presetGreenRedSingles(system):
    green = (0, 255, 0)
    off = (0, 0, 0)
    red = (255, 0, 0)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[green, off, off, off, off, off, red,
                    off, off, off, off, off, off, off, off],
            multiplier=1,
            speed=1),
        15)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[green, None, None, None, None, None, None, None],
            multiplier=1,
            speed=-10),
        16)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[red, None, None, None, None, None, None, None, None],
            multiplier=1,
            speed=20),
        16)


def presetStars(system):
    off = (0, 0, 0)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[(255, 255, 255), off, off, off, off, off, off, off, off, off,
                    (200, 200, 200), off, off, off, off, off, off,
                    (150, 150, 150), off, off, off, off, off, off, off, off, off, off, off],
            multiplier=1,
            speed=1),
        15)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[(100, 100, 100), None, None, off, None, None, None, off, None, None, None, off, None,
                    (200, 200, 200), off, None, None,
                    (150, 150, 150), None, None, None, None, off, off, None, None, off],
            multiplier=1,
            speed=-0.5),
        16)


def presetBluesColors(system):
    blue = (0, 47, 135)
    navy = (4, 30, 66)
    yellow = (252, 181, 20)
    white = (255, 255, 255)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[navy, white, blue, blue, yellow],
            multiplier=6,
            speed=1),
        15)


def presetChiefsColors(system):
    red = (255, 0, 0)
    yellow = (252, 181, 20)
    white = (255, 255, 255)
    system.getComponentByName("top_row").addProgram(
        PatternProgram(
            colors=[red, red, white, yellow, red, red, yellow, white],
            multiplier=6,
            speed=20),
        15)
    system.getComponentByName("bottom_row").addProgram(
        PatternProgram(
            colors=[red, red, white, yellow, red, red, yellow, white],
            multiplier=6,
            speed=-20),
        15)


def presetRedWhiteStill(system):
    red = (255, 0, 0)
    white = (255, 210, 120)
    off = (0, 0, 0)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[red, off, white, off],
            multiplier=2,
            speed=0.1),
        15)


def presetSolidWhite(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=20,
            gap_length=0,
            stripe_rgb=[255, 255, 255]))


def presetSolidBlue(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=20,
            gap_length=0,
            stripe_rgb=[0, 0, 255]))


def presetSolidGreen(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=20,
            gap_length=0,
            stripe_rgb=[0, 255, 0]))


def presetSolidRed(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=20,
            gap_length=0,
            stripe_rgb=[255, 0, 0]))


def presetCandycane(system):
    gap = 30
    stripe = 6
    system.getComponentByName("bottom_row").addProgram(
        GradientProgram(speed=-5,
                        length=55,
                        start_color=(-100, -100, -100)),
        10)
    system.getComponentByName("bottom_row").addProgram(
        CandyCaneProgram(
            stripe_length=stripe,
            gap_length=gap,
            gap_rgb=None),
        20)
    system.getComponentByName("bottom_row").addProgram(
        CandyCaneProgram(
            stripe_length=stripe,
            offset=(gap+stripe)/2,
            stripe_rgb=(0, 255, 0),
            gap_length=gap,
            gap_rgb=None),
        21)
    system.getComponentByName("top_row").addProgram(
        GradientProgram(speed=5,
                        length=55,
                        start_color=(-100, -100, -100)),
        10)
    system.getComponentByName("top_row").addProgram(
        CandyCaneProgram(
            stripe_length=stripe,
            speed=-10,
            gap_length=gap,
            gap_rgb=None),
        20)
    system.getComponentByName("top_row").addProgram(
        CandyCaneProgram(
            stripe_length=stripe,
            offset=(gap+stripe)/2,
            stripe_rgb=(0, 255, 0),
            speed=-10,
            gap_length=gap,
            gap_rgb=None),
        21)


def start_webserver():
    global http_server
    http_server = HTTPServerWrapper()
    http_server.start(system)


def start_websocket():
    global websocket_server
    websocket_server = WebSocketServer()
    websocket_server.leds = led_count
    websocket_server.start()


if __name__ == "__main__":
    def onUpdate(colors):
        """
        Updates the entire strip of lights all at once.
        More bandwidth, but less processing/memory used on server.
        """
        if websocket_server:
            websocket_server.send(json.dumps({
                "colors": colors
            }))

    def canSendUpdate():
        if websocket_server == None:
            return False
        return websocket_server.connection != None

    system = LEDSystem(led_count=led_count)
    system.onChangeListener = onUpdate
    system.canSendUpdate = canSendUpdate
    system.configure(componentConfig)
    # system.registerPreset(preset1, "Demo")
    system.registerPreset(presetStars, "Stars")
    system.registerPreset(presetBlueWhiteLong, "Blue/Whiiiiiite")
    system.registerPreset(presetRedWhiteStill, "Red/White still")
    system.registerPreset(presetGreenRedSingles, "Red/Green dots")
    system.registerPreset(presetBlueWhiteSingles, "Blue/White dots")
    system.registerPreset(presetBlueWhiteShort, "Blue/White")
    system.registerPreset(presetBlueOffShort, "Blue/Off")
    system.registerPreset(presetSolidBlue, "Blue")
    system.registerPreset(presetSolidRed, "Red")
    system.registerPreset(presetSolidGreen, "Green")
    system.registerPreset(presetSolidWhite, "White")
    system.registerPreset(presetRedGreen, "Red/Green")
    system.registerPreset(presetChiefsColors, "Chiefs")
    system.registerPreset(presetBluesColors, "Blues")
    system.registerPreset(presetThanksgiving, "Thanksgiving")
    system.registerPreset(presetCandycane, "Candycane")
    system.start()

    # Start web server and websocket server on separate threads
    threading.Thread(target=start_webserver, name="http-server").start()
    threading.Thread(target=start_websocket, name="websocket-server").start()
