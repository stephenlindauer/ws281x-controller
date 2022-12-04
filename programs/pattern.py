from programs.program import Program
try:
    from rpi_ws281x import Color
except Exception:
    from rpi_stub import Color


class PatternProgram(Program):
    def __init__(self,
                 colors=[],
                 multiplier=1,
                 offset=0,
                 speed=0,
                 program_range=None,
                 ):
        super().__init__("pattern", program_range)

        self.colors = colors
        self.multiplier = multiplier
        self.offset = offset
        self.speed = speed

    def update(self, it):
        cycle = len(self.colors) * self.multiplier

        p = int(self.offset + it *
                (self.speed / self.system.ups)) % cycle - cycle
        while p <= self.component.length:
            for i in range(0, len(self.colors)):
                color = self.colors[i]
                if color:
                    self.paint(
                        Color(int(color[0]), int(color[1]), int(color[2])),
                        range(p + (i * self.multiplier),
                              p + ((i+1) * self.multiplier))
                    )
            p += cycle
