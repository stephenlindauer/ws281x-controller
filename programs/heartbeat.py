from programs.program import Program
try:
    from rpi_ws281x import Color
except Exception:
    from rpi_stub import Color


class HeartbeatProgram(Program):
    heartbeatBrightness = 255

    def __init__(self):
        super().__init__("heartbeat")

    def update(self, it):
        step = 70
        if (it % step == 0):
            self.heartbeatBrightness = 0
        if (it % step < 10):
            self.heartbeatBrightness += 25
        elif (it % step < 20):
            self.heartbeatBrightness -= 16
        elif (it % step < 30):
            self.heartbeatBrightness += 16
        elif (it % step < 80):
            self.heartbeatBrightness -= 6
        self.heartbeatBrightness = max(min(self.heartbeatBrightness, 255), 0)
        self.paint(Color(int(self.heartbeatBrightness), 0, 0))
