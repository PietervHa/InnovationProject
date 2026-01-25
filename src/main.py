from drone_controller import DroneController
import time


def main():
    drone = DroneController()
    drone.connect()

    time.sleep(2)
    drone.takeoff()

    time.sleep(3)
    drone.land()


if __name__ == "__main__":
    main()
