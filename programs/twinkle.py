from programs.program import Program
from led_system import LEDSystem

try:
    from rpi_ws281x import Color
except Exception:
    from rpi_stub import Color

import random


class TwinkleProgram(Program):
    def __init__(self,
                 colors=[],
                 multiplier=1,
                 offset=0,
                 speed=0,
                 program_range=None,
                 ):
        super().__init__("twinkle", program_range)

        self.colors = colors
        self.multiplier = multiplier
        self.offset = offset
        self.speed = speed
        self.alphas = []

    def registerSystem(self, system: LEDSystem):
        super().registerSystem(system)
        for i in range(0, system.led_count):
            self.alphas.append(random.randint(0, 199))

    def update(self, it):
        cycle = len(self.colors) * self.multiplier

        p = int(self.offset + it *
                (self.speed / self.system.ups)) % cycle - cycle
        while p <= self.component.length:
            for i in range(0, len(self.colors)):
                idx = p + (i * self.multiplier)
                try:
                    a = self.alphas[idx]

                    # Wrap
                    if a > 200:
                        a = 0

                    self.alphas[idx] = a+1
                    a = a/100
                    if a > 1:
                        a = 2-a

                except:
                    a = 0

                color = self.colors[i]
                if color:
                    self.paint(
                        Color(int(color[0] * a),
                              int(color[1] * a),
                              int(color[2] * a)),
                        range(p + (i * self.multiplier),
                              p + ((i+1) * self.multiplier))
                    )
            p += cycle
