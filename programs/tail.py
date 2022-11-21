from programs.program import Program
try:
    from rpi_ws281x import Color
except Exception:
    from rpi_stub import Color


class TailProgram(Program):
    def __init__(self,
                 length=30,
                 offset=0,
                 speed=1,
                 rgb=[255, 255, 255],
                 fade=True,
                 program_range=None):
        super().__init__("tail", program_range)

        self.length = length
        self.offset = offset
        self.speed = speed
        self.rgb = rgb
        self.fade = fade

    def update(self, it):
        effective_range = self.program_range or range(0, self.component.length)

        for i in range(0, self.length):
            p = int(((it * (self.speed / self.system.ups)) - i +
                     self.offset)) % (effective_range.stop - effective_range.start) + effective_range.start

            pct = (1 - i / self.length) if self.fade else 1
            self.paint(
                Color(
                    int(self.rgb[0] * pct),
                    int(self.rgb[1] * pct),
                    int(self.rgb[2] * pct)
                ),
                range(p, p + 1)
            )
