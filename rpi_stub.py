def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return (white << 24) | (red << 16) | (green << 8) | blue


class Adafruit_NeoPixel:
    def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False,
                 brightness=255, channel=0, strip_type=None, gamma=None):
        pass

    def begin(self):
        pass

    def show(self):
        pass

    def setPixelColor(self, i, color):
        pass


WS2811_STRIP_RGB = None
