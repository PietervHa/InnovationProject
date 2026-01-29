from src.drone_controller import DroneController
import time
import threading
import keyboard
import sys

# Variabele om vlucht te stoppen
emergency_triggered = False

# ==============================
# EMERGENCY STOP LISTENER
# ==============================
def listen_for_emergency(drone):
    global emergency_triggered
    keyboard.wait('e')
    print("EMERGENCY STOP ACTIVATED")
    emergency_triggered = True
    drone.emergency_stop()


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

# Start noodstop listener op achtergrond
threading.Thread(target=listen_for_emergency, args=(drone,), daemon=True).start()

print("Demo gestart — druk op 'E' voor NOODSTOP")

for step in demo_route:
    if emergency_triggered:
        print("Vlucht afgebroken door noodstop")
        sys.exit()

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

print("Demo voltooid")
