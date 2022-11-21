from led_system import LEDSystem, LEDComponentObject


class Program():
    name = ""
    system: LEDSystem
    component: LEDComponentObject
    program_range = None

    def __init__(self, name, program_range=None):
        self.name = name
        self.program_range = program_range

    def registerSystem(self, system: LEDSystem):
        self.system = system

    def registerComponent(self, component: LEDComponentObject):
        self.component = component

    def update(self):
        pass

    def paint(self, color, lightRange=None):
        if (lightRange and self.program_range):
            # find intersections
            intersection = range(
                max(lightRange[0], self.program_range[0]),
                min(lightRange[-1], self.program_range[-1])+1)
            if (intersection.stop-intersection.start > 0):
                self.component.paint(color, intersection)

            pass
        elif (self.program_range):
            # No range provided to paint(), use program
            self.component.paint(color, self.program_range)
        else:
            # No program_range or no ranges at all, paint it all
            self.component.paint(color, lightRange)
