from enum import Enum
try:
    from rpi_ws281x import Color
except Exception:
    from rpi_stub import Color


class NamedColor():
    OFF = Color(0, 0, 0)
    BLACK = OFF
    RED = Color(255, 0, 0)
    BLUE = Color(0, 0, 255)
    GREEN = Color(0, 255, 0)
    WHITE = Color(255, 255, 255)
    WHITE2 = Color(255, 255, 230)
