from src.drone_controller import DroneController
import time

drone = DroneController()
drone.connect()

time.sleep(2)
drone.takeoff()

time.sleep(2)
drone.move("forward", 50)

time.sleep(2)
drone.rotate(90)

time.sleep(2)
drone.move("left", 30)

time.sleep(2)
drone.land()
