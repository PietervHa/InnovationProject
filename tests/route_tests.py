from src.drone_controller import DroneController
import time

# Definitie van een automatische vluchtroute
route = [
    ("takeoff", None),
    ("move", ("forward", 50)),
    ("rotate", 90),
    ("move", ("right", 30)),
    ("move", ("backward", 40)),
    ("land", None)
]

drone = DroneController()
drone.connect()

for step in route:
    action = step[0]
    value = step[1]

    if action == "takeoff":
        drone.takeoff()
    elif action == "land":
        drone.land()
    elif action == "move":
        direction, distance = value
        drone.move(direction, distance)
    elif action == "rotate":
        drone.rotate(value)

    time.sleep(2)
