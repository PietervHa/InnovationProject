import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import threading
import time

from src.drone_controller import DroneController


class DroneUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tello Drone Controller")
        self.root.geometry("700x600")

        self.drone = DroneController()
        self.connected = False
        self.video_running = False

        # ===== BATTERIJ =====
        self.battery_label = tk.Label(root, text="Battery: --%", font=("Arial", 14))
        self.battery_label.pack(pady=5)

        tk.Button(root, text="Connect Drone", command=self.connect_drone, bg="lightblue").pack(pady=5)

        # ===== VIDEO CANVAS =====
        self.video_label = tk.Label(root)
        self.video_label.pack(pady=10)

        # ===== VLUCHT KNOPPEN =====
        tk.Button(root, text="Takeoff", command=self.takeoff, bg="lightgreen").pack(pady=5)
        tk.Button(root, text="Land", command=self.land, bg="orange").pack(pady=5)

        movement_frame = tk.Frame(root)
        movement_frame.pack(pady=10)

        tk.Button(movement_frame, text="↑ Forward", command=lambda: self.move("forward")).grid(row=0, column=1)
        tk.Button(movement_frame, text="← Left", command=lambda: self.move("left")).grid(row=1, column=0)
        tk.Button(movement_frame, text="Right →", command=lambda: self.move("right")).grid(row=1, column=2)
        tk.Button(movement_frame, text="↓ Backward", command=lambda: self.move("backward")).grid(row=2, column=1)

        tk.Button(root, text="⟲ Rotate Left", command=lambda: self.rotate(-90)).pack(pady=5)
        tk.Button(root, text="⟳ Rotate Right", command=lambda: self.rotate(90)).pack(pady=5)

        tk.Button(root, text="EMERGENCY STOP", command=self.emergency, bg="red", fg="white").pack(pady=20)

    # =============================

    def connect_drone(self):
        try:
            self.drone.connect()
            self.drone.stream_on()
            self.connected = True
            self.video_running = True

            messagebox.showinfo("Connected", "Drone connected & video started!")

            threading.Thread(target=self.update_battery, daemon=True).start()
            threading.Thread(target=self.video_loop, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_battery(self):
        while self.connected:
            battery = self.drone.get_battery()
            self.battery_label.config(text=f"Battery: {battery}%")
            time.sleep(5)

    def video_loop(self):
        while self.video_running:
            frame = self.drone.get_frame()

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            time.sleep(0.03)

    # ===== DRONE COMMANDS =====

    def takeoff(self):
        if self.connected:
            self.drone.takeoff()

    def land(self):
        if self.connected:
            self.drone.land()

    def move(self, direction):
        if self.connected:
            self.drone.move(direction, 30)

    def rotate(self, angle):
        if self.connected:
            self.drone.rotate(angle)

    def emergency(self):
        if self.connected:
            self.drone.emergency_stop()


if __name__ == "__main__":
    root = tk.Tk()
    app = DroneUI(root)
    root.mainloop()
