from programs.program import Program
try:
    from rpi_ws281x import Color
except Exception:
    from rpi_stub import Color


class GradientProgram(Program):
    def __init__(self,
                 start_color=(0, 0, 0),
                 stop_color=(255, 255, 255),
                 length=50,
                 speed=0,
                 offset=0,
                 program_range=None,
                 ):
        super().__init__("gradient", program_range)

        self.start_color = start_color
        self.stop_color = stop_color
        self.length = length
        self.speed = speed
        self.offset = offset

    def update(self, it):
        cycle = self.length

        p = int(self.offset + it *
                (self.speed / self.system.ups)) % cycle - cycle
        while p <= self.component.length:
            for i in range(0, int(cycle / 2)+1):
                color = (
                    self.start_color[0] * (1-i/(cycle/2)) +
                    self.stop_color[0] * i/(cycle/2),
                    self.start_color[1] * (1-i/(cycle/2)) +
                    self.stop_color[1] * i/(cycle/2),
                    self.start_color[2] * (1-i/(cycle/2)) +
                    self.stop_color[2] * i/(cycle/2),
                )
                self.paint(
                    Color(
                        min(255, max(0, int(color[0]))),
                        min(255, max(0, int(color[1]))),
                        min(255, max(0, int(color[2])))),
                    range(p + i, p + i+1)
                )
                self.paint(
                    Color(
                        min(255, max(0, int(color[0]))),
                        min(255, max(0, int(color[1]))),
                        min(255, max(0, int(color[2])))),
                    range(p + cycle - i, p + cycle - i + 1)
                )
            p += cycle
