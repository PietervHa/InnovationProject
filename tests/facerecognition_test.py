from djitellopy import Tello
import cv2

# Initialiseer drone
drone = Tello()
drone.connect()
print(f"Battery: {drone.get_battery()}%")

# Start videostream
drone.streamon()
frame_reader = drone.get_frame_read()

# Haarcascade voor gezichtsdetectie
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

print("Press 'q' to stop")

while True:
    frame = frame_reader.frame

    if frame is None:
        continue

    # Converteer naar grijs voor detectie
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detecteer gezichten
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(60, 60)
    )

    # Teken rechthoek om elk gezicht
    for (x, y, w, h) in faces:
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    # Toon beeld
    cv2.imshow("Tello Face Detection", frame)

    # Stop met 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Opruimen
cv2.destroyAllWindows()
drone.streamoff()
drone.end()
