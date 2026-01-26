from src.drone_controller import DroneController
import time

# Definitieve demo-vluchtroute
demo_route = [
    ("takeoff", None),
    ("move", ("forward", 40)),
    ("rotate", 90),
    ("move", ("left", 30)),
    ("rotate", -90),
    ("move", ("backward", 40)),
    ("land", None)
]

drone = DroneController()
drone.connect()

for step in demo_route:
    action, value = step

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
