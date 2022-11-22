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
led_count = 1000

componentConfig = {
    "components": [
        {
            "label": "root",
            "light_begin": "infer",
            "length": "infer",
            "components": [
                {
                    "label": "section1",
                    "light_begin": 0,
                    "length": 50
                },
                {
                    "label": "section2",
                    "light_begin": 50,
                    "length": 150,
                },
                {
                    "label": "section3",
                    "light_begin": 200,
                    "length": 150
                },
                {
                    "label": "section4",
                    "light_begin": 350,
                    "length": 150
                },
                {
                    "label": "section5",
                    "light_begin": 500,
                    "length": 150
                },
                {
                    "label": "section6",
                    "light_begin": 650,
                    "length": 150
                },
                {
                    "label": "section7",
                    "light_begin": 800,
                    "length": 200
                },
            ]
        },
    ]
}


def preset1(system):
    system.getComponentByName("root").addProgram(
        TailProgram(
            length=10,
            rgb=[0, 0, 255],
            speed=40),
        25)
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=10,
            gap_length=33,
            program_range=range(300, 1000)),
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


def preset2(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=2,
            gap_length=2,
            stripe_rgb=[0, 0, 255]))


def preset3(system):
    system.getComponentByName("root").addProgram(
        CandyCaneProgram(
            stripe_length=20,
            gap_length=20,
            stripe_rgb=[0, 255, 0],
            gap_rgb=[255, 0, 0]))

    system.getComponentByName("section3").addProgram(
        CandyCaneProgram(
            stripe_length=14,
            gap_length=1,
            speed=-10,
            stripe_rgb=[0, 150, 0],
            gap_rgb=[255, 0, 0]))


def presetBluesColors(system):
    blue = (0, 47, 135)
    navy = (4, 30, 66)
    yellow = (252, 181, 20)
    white = (255, 255, 255)
    system.getComponentByName("root").addProgram(
        PatternProgram(
            colors=[navy, white, yellow, blue],
            multiplier=5,
            speed=1),
        15)


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

    system = LEDSystem(led_count=led_count)
    system.onChangeListener = onUpdate
    system.configure(componentConfig)
    system.registerPreset(preset1, "demo")
    system.registerPreset(preset2, "blue-white")
    system.registerPreset(preset3, "red-green")
    system.registerPreset(presetBluesColors, "blues")
    system.start()

    # Start web server and websocket server on separate threads
    threading.Thread(target=start_webserver, name="http-server").start()
    threading.Thread(target=start_websocket, name="websocket-server").start()
