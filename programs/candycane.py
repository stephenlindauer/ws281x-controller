from programs.program import Program
try:
    from rpi_ws281x import Color
except Exception:
    from rpi_stub import Color


class CandyCaneProgram(Program):
    def __init__(self,
                 stripe_length=30,
                 gap_length=30,
                 offset=0,
                 speed=10,
                 stripe_rgb=[255, 0, 0],
                 gap_rgb=[255, 255, 255],
                 program_range=None,
                 ):
        super().__init__("candycane", program_range)

        self.stripe_length = stripe_length
        self.gap_length = gap_length
        self.offset = offset
        self.speed = speed
        self.stripe_rgb = stripe_rgb
        self.gap_rgb = gap_rgb

    def update(self, it):
        # Paint the entire gap in one go
        if (self.gap_rgb):
            self.paint(
                Color(self.gap_rgb[0], self.gap_rgb[1], self.gap_rgb[2]))

        cycle = self.stripe_length + self.gap_length

        p = int(self.offset + it *
                (self.speed / self.system.ups)) % cycle - cycle
        while p <= self.component.length:
            self.paint(
                Color(
                    int(self.stripe_rgb[0]),
                    int(self.stripe_rgb[1]),
                    int(self.stripe_rgb[2])
                ),
                range(p, p + self.stripe_length)
            )
            p += cycle
