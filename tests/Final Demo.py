from djitellopy import Tello
import cv2
import threading
import keyboard
import sys
import time

# ==============================
# 🚨 EMERGENCY STOP VARIABLES
# ==============================
emergency_triggered = False
face_detected = False

# ==============================
# 🚨 EMERGENCY STOP THREAD
# ==============================
def emergency_listener(drone):
    """
    Luistert naar 'E' toets voor noodstop.
    """
    global emergency_triggered
    keyboard.wait('e')
    print("🚨 EMERGENCY STOP ACTIVATED!")
    emergency_triggered = True
    drone.emergency_stop()

# ==============================
# 👀 GEZICHTSDETECTIE THREAD
# ==============================
def face_detection_thread(drone):
    """
    Detecteert gezichten en toont live video.
    Zodra een gezicht wordt gedetecteerd, wordt de vlucht afgebroken.
    """
    global face_detected
    frame_reader = drone.get_frame_read()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    while not face_detected and not emergency_triggered:
        frame = frame_reader.frame
        if frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

        if len(faces) > 0:
            print("👤 Gezicht gedetecteerd! Vlucht wordt afgebroken.")
            face_detected = True

        # Rechthoek rond gezichten (voor live video)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Tello Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# ==============================
# 🟢 DRONE INITIALISATIE
# ==============================
drone = Tello()
drone.connect()
print(f"Battery: {drone.get_battery()}%")
drone.streamon()

# Start emergency en face detection threads
threading.Thread(target=emergency_listener, args=(drone,), daemon=True).start()
threading.Thread(target=face_detection_thread, args=(drone,), daemon=True).start()

# ==============================
# 🔵 VLUCHTROUTE
# ==============================
route = [
    ("takeoff", None),
    ("move_forward", 50),
    ("rotate", 90),
    ("move_left", 40),
    ("rotate", -90),
    ("move_forward", 30),
]

print("Demo gestart — druk op 'E' voor noodstop, 'q' om venster te sluiten")

for step in route:
    if emergency_triggered:
        print("🛑 Vlucht afgebroken door noodstop!")
        break

    if face_detected:
        print("🛑 Vlucht afgebroken door gezichtsdetectie! Drone vliegt achteruit en landt.")
        drone.move_back(40)
        time.sleep(1)
        drone.land()
        sys.exit()

    action, value = step

    if action == "takeoff":
        drone.takeoff()
    elif action == "move_forward":
        drone.move_forward(value)
    elif action == "move_back":
        drone.move_back(value)
    elif action == "move_left":
        drone.move_left(value)
    elif action == "move_right":
        drone.move_right(value)
    elif action == "rotate":
        if value > 0:
            drone.rotate_clockwise(value)
        else:
            drone.rotate_counter_clockwise(-value)

    time.sleep(2)

# Als geen gezichtsdetectie of noodstop
if not face_detected and not emergency_triggered:
    drone.land()
    print("Route voltooid zonder detectie")

# ==============================
# 🔴 OPRUIMEN
# ==============================
cv2.destroyAllWindows()
drone.streamoff()
drone.end()
