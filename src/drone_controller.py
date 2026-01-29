from djitellopy import Tello


class DroneController:
    def __init__(self):
        self.drone = Tello()

    def connect(self):
        self.drone.connect()
        battery = self.drone.get_battery()
        print(f"Battery level: {battery}%")

    def takeoff(self):
        self.drone.takeoff()

    def land(self):
        self.drone.land()

    def emergency_stop(self):
        self.drone.emergency()

    def move(self, direction: str, distance: int):
        if direction == "forward":
            self.drone.move_forward(distance)
        elif direction == "backward":
            self.drone.move_back(distance)
        elif direction == "left":
            self.drone.move_left(distance)
        elif direction == "right":
            self.drone.move_right(distance)
        elif direction == "up":
            self.drone.move_up(distance)
        elif direction == "down":
            self.drone.move_down(distance)
        else:
            raise ValueError(f"Invalid direction: {direction}")

    def rotate(self, angle: int):
        if angle > 0:
            self.drone.rotate_clockwise(angle)
        else:
            self.drone.rotate_counter_clockwise(abs(angle))
