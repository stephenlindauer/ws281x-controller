from programs.program import Program
from named_colors import NamedColor


class StrobeProgram(Program):
    def __init__(self):
        super().__init__("strobe")

    def update(self, it):
        step = 26
        if (it % step < 6):
            self.paint(NamedColor.WHITE2)
        elif (it % step < 10):
            self.paint(NamedColor.OFF)
        elif (it % step < 13):
            self.paint(NamedColor.OFF)
        elif (it % step < 16):
            self.paint(NamedColor.WHITE2)
        elif (it % step < 19):
            self.paint(NamedColor.OFF)
        elif (it % step < 22):
            self.paint(NamedColor.WHITE2)
        else:
            self.paint(NamedColor.OFF)
