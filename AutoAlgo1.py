class AutoAlgo1:
    def __init__(self, map):
        self.map = map
        self.speed = 1
        self.spin_angle = 0
        self.counter = 0
        self.is_risky = False
        self.risky_dis = 0

    def speed_up(self):
        self.speed += 1
        print(f"Speed increased to {self.speed}")

    def speed_down(self):
        self.speed -= 1
        print(f"Speed decreased to {self.speed}")

    def spin_by(self, angle):
        self.spin_angle += angle
        print(f"Spun by {angle} degrees")

    def update(self):
        # Update the drone's state
        self.counter += 1

    def get_info_html(self):
        return f"<html>Speed: {self.speed}<br>Spin Angle: {self.spin_angle}<br>Counter: {self.counter}</html>"
