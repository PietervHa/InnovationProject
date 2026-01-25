from src.drone_controller import DroneController
import time

drone = DroneController()
drone.connect()

time.sleep(2)
drone.takeoff()

time.sleep(3)
drone.land()
