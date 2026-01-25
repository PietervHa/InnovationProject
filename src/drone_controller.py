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
