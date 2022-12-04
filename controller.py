#!/usr/bin/env python3

# How to Start/Stop service:
# sudo systemctl start lights
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
led_count = 277

componentConfig = {
    "components": [
        {
            "label": "root",
            "light_begin": "infer",
            "length": 277,
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
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=2,
            gap_length=2,
            stripe_rgb=[0, 0, 255]))


def presetBlueWhiteLong(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=2,
            gap_length=9,
            stripe_rgb=[0, 0, 255]))


def presetRedGreen(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=20,
            gap_length=20,
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
            colors=[green, off, off, off, red, off, off, off, off, off, off],
            multiplier=1,
            speed=1),
        15)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[green, None, None, None, None, None],
            multiplier=1,
            speed=-10),
        16)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[red, None, None, None, None, None, None],
            multiplier=1,
            speed=20),
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
    system.getComponentByName("root").addProgram(
        GradientProgram(speed=-5, length=50),
        10)
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=6,
            gap_length=20,
            gap_rgb=None),
        20)


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
    system.registerPreset(presetBlueWhiteLong, "Blue/Whiiiiiite")
    system.registerPreset(presetGreenRedSingles, "Red/Green dots")
    system.registerPreset(presetBlueWhiteSingles, "Blue/White dots")
    system.registerPreset(presetBlueWhiteShort, "Blue/White")
    system.registerPreset(presetBlueOffShort, "Blue/Off")
    system.registerPreset(presetSolidBlue, "Blue")
    system.registerPreset(presetSolidRed, "Red")
    system.registerPreset(presetSolidGreen, "Green")
    system.registerPreset(presetSolidWhite, "White")
    system.registerPreset(presetRedGreen, "Red/Green")
    system.registerPreset(presetBluesColors, "Blues")
    system.registerPreset(presetThanksgiving, "Thanksgiving")
    system.registerPreset(presetCandycane, "Candycane")
    system.start()

    # Start web server and websocket server on separate threads
    threading.Thread(target=start_webserver, name="http-server").start()
    threading.Thread(target=start_websocket, name="websocket-server").start()
