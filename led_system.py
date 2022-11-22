import logging
try:
    from rpi_ws281x import Adafruit_NeoPixel, WS2811_STRIP_RGB
except Exception:
    logging.warning("Missing rpi_ws281x package, using stubs instead")
    # This happens when running on a platform which doesn't have rpi_ws281x support
    # This allows us to run everything in a simulated environment so we just stub out
    # the calls here.
    from rpi_stub import Adafruit_NeoPixel, WS2811_STRIP_RGB
from threading import Timer
from typing import Callable, Optional
from named_colors import NamedColor
from datetime import datetime


class LEDComponentObject:
    components: list["LEDComponentObject"]
    programs: dict[int, list]

    def __init__(self, system: "LEDSystem", label: str, light_begin: int, length: int):
        self.system = system
        self.label = label
        self.light_begin = light_begin
        self.length = length
        self.components = []
        self.programs = {}

    def toJSON(self):
        return {
            "label": self.label,
            "begin": self.light_begin,
            "length": self.length,
            "components": list(map(lambda c: c.toJSON(), self.components))
        }

    def update(self, it: int):
        # Draw from programs first
        depths = list(self.programs.keys())
        depths.sort()
        for depth in depths:
            for p in self.programs[depth]:
                # Timing perf logging
                # time_start = datetime.now()
                p.update(it)
                # time_spent = datetime.now() - time_start
                # time_spent_ms = time_spent.seconds * 1000 + time_spent.microseconds / 1000
                # print("[DEBUG] %s update took %dms" % (p.name, time_spent_ms))

        # Then draw child components
        for component in self.components:
            component.update(it)

    def addProgram(self, program, depth=1):
        """Adds"""
        program.registerComponent(self)
        program.registerSystem(self.system)
        if depth not in self.programs:
            # Create empty list at this depth if nothing here
            self.programs[depth] = []
        self.programs[depth].append(program)

    def paint(self, color, lightRange=None):
        """Paints a range of leds a single color"""
        if not lightRange:
            r = range(self.light_begin, self.light_begin + self.length)
        else:
            r = range(self.light_begin + max(0, lightRange.start),
                      min(self.light_begin + self.length, lightRange.stop + self.light_begin))
        for i in r:
            self.system._setPixelColor(i, color, True)

    def clearPrograms(self):
        for depth in self.programs.keys():
            self.programs[depth] = []
        for component in self.components:
            component.clearPrograms()


class LEDSystem:
    ups = 20  # Updates per Second
    strip = None
    led_count: int
    programs: dict[int, list] = {}
    components: list[LEDComponentObject] = []
    componentMap: dict[str, LEDComponentObject] = {}
    onChangeListener: Callable[[int], None]
    canSendUpdate: Callable[[], bool]
    ledColor: dict[int, int] = {}
    SIMULATE = False
    it: int = 0
    enabled: bool = True
    presetFunctions: dict[str, Callable] = {}
    currentPreset: str
    isUpdating: bool = False

    def __init__(self, led_count=600, skip_intro=False, simulate=False):
        self.led_count = led_count
        self.SIMULATE = simulate
        self.setupStrip()
        self.lights = []
        self.nextId = 1
        self.currentPreset = None
        for i in range(0, led_count):
            self.ledColor[i] = -1

    def start(self):
        if self.currentPreset == None:
            # Use first preset if we don't have one yet
            self.usePreset(next(iter(self.presetFunctions)))

        self._update()

    def _update(self):
        self.it += 1
        self._timer = Timer(1 / self.ups, self._update)
        self._timer.start()
        time_start = datetime.now()
        max_time_ms = 1/self.ups*1000
        try:
            if self.isUpdating:
                logging.warning(
                    "Last update operation is still in progress, skip frame")
                return
            self.isUpdating = True
            self.update()
            self.strip.show()

            time_spent = datetime.now() - time_start
            time_spent_ms = time_spent.seconds * 1000 + time_spent.microseconds / 1000
            if (time_spent_ms > max_time_ms):
                """
                If you end up hitting this warning often, it means your draw operations are too expensive.
                Consider reducing the complexity of your programs or lower the updates per second (ups).
                """
                logging.warning("Spent %dms updating which is longer than a single draw cycle of %dms" % (
                    time_spent.seconds * 1000 + time_spent.microseconds / 1000, max_time_ms))
            self.notifyChanges()
            # print("[DEBUG] time spent updating: %dms" % time_spent_ms)
            self.isUpdating = False
        except Exception as e:
            print("update() Exception: " + str(e))
            self.isUpdating = False

    def setStripEnabled(self, enabled: bool):
        self.enabled = enabled

    def update(self):
        if (self.enabled):
            for component in self.components:
                component.update(self.it)
        else:
            self.paint(NamedColor.OFF)

    def notifyChanges(self):
        if self.canSendUpdate():
            self.onChangeListener(list(self.ledColor.values()))

    def configure(self, config):
        for c in config["components"]:
            self.components.append(self.parseComponentFromConfig(c))

    def registerPreset(self, preset, presetName):
        self.presetFunctions[presetName] = preset

    def usePreset(self, presetName):
        # Clear previous programs
        for component in self.components:
            component.clearPrograms()
        self.paint(NamedColor.OFF)

        self.currentPreset = presetName
        self.presetFunctions[presetName](self)

    def parseComponentFromConfig(self, c) -> LEDComponentObject:
        # Validation
        if "label" not in c:
            logging.warning('Component is missing a label')
        if c["label"] in self.componentMap:
            logging.warning(
                'Label %s was reused which is not allowed' % c["label"])
        if c["light_begin"] == 'infer' or c["length"] == 'infer':
            if 'components' not in c:
                logging.warning(
                    "Cannot infer begin/end without child components")

        # Create the component
        component = LEDComponentObject(self,
                                       c["label"], c["light_begin"], c["length"])
        # Register component by label
        self.componentMap[component.label] = component

        # Create nested components
        if ("components" in c):
            min_light = int('inf')
            max_light_end = int('-inf')
            for child in c["components"]:
                child_component = self.parseComponentFromConfig(child)
                component.components.append(child_component)
                min_light = min(min_light, child_component.light_begin)
                max_light_end = max(
                    max_light_end, child_component.light_begin + child_component.length)
            if component.light_begin == 'infer':
                component.light_begin = min_light
            if component.length == 'infer':
                component.length = max_light_end
        return component

    def paint(self, color, lightRange=None):
        """Paints a range of leds a single color"""
        if not lightRange:
            r = range(self.led_count)
        else:
            r = lightRange
        for i in r:
            self._setPixelColor(i, color, True)

    def addProgram(self, program, depth=1):
        """Adds"""
        program.registerSystem(self)
        if depth not in self.programs:
            # Create empty list at this depth if nothing here
            self.programs[depth] = []
        self.programs[depth].append(program)

    def setupStrip(self):
        """Setup of the rpi_ws281x strip"""
        # LED strip configuration:
        # 18      # GPIO pin connected to the pixels (18 uses PWM!).
        LED_PIN = 12
        # LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10        # DMA channel to use for generating signal (try 10)

        LED_BRIGHTNESS = 100
        # Set to 0 for darkest and 255 for brightest
        # True to invert the signal (when using NPN transistor level shift)
        LED_INVERT = False
        LED_CHANNEL = 0     # set to '1' for GPIOs 13, 19, 41, 45 or 53

        self.strip = Adafruit_NeoPixel(self.led_count, LED_PIN, LED_FREQ_HZ,
                                       LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, strip_type=WS2811_STRIP_RGB)
        self.strip.begin()

    def getComponentByName(self, name) -> Optional[LEDComponentObject]:
        if name not in self.componentMap:
            logging.warning("Component not found: %s" % name)
        return self.componentMap[name]

    def _setPixelColor(self, i, color, ignore_block_list=False):
        block_list = list(range(420, 500))
        if i not in range(0, self.led_count):
            return
        if i in block_list and not ignore_block_list:
            return
        self.ledColor[i] = color
        self.strip.setPixelColor(i, color)
