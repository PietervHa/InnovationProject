import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import cv2
import threading
import time

from src.drone_controller import DroneController


class DroneUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tello Drone Controller")
        self.root.geometry("900x500")

        self.drone = DroneController()
        self.connected = False
        self.video_running = False

        # ===== MAIN LAYOUT: left (video) + right (controls) =====
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== LEFT: VIDEO FEED =====
        left_frame = tk.Frame(main_frame, bg="black", width=640, height=480)
        left_frame.pack(side="left", fill="both", expand=True)
        left_frame.pack_propagate(False)  # Keep fixed size even when empty

        self.video_label = tk.Label(left_frame, bg="black")
        self.video_label.pack(expand=True)

        # ===== RIGHT: CONTROLS =====
        right_frame = tk.Frame(main_frame, padx=10)
        right_frame.pack(side="right", fill="y")

        # Battery
        self.battery_label = tk.Label(right_frame, text="Battery: --%", font=("Arial", 13))
        self.battery_label.pack(pady=(0, 5))

        # Connect
        tk.Button(right_frame, text="Connect Drone", command=self.connect_drone,
                  bg="lightblue", width=18).pack(pady=5)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=8)

        # Takeoff / Land
        tk.Button(right_frame, text="Takeoff", command=self.takeoff,
                  bg="lightgreen", width=18).pack(pady=3)
        tk.Button(right_frame, text="Land", command=self.land,
                  bg="orange", width=18).pack(pady=3)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=8)

        # Movement grid
        movement_frame = tk.Frame(right_frame)
        movement_frame.pack(pady=5)

        btn_cfg = {"width": 10, "height": 2}
        tk.Button(movement_frame, text="↑ Forward",
                  command=lambda: self.move("forward"), **btn_cfg).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(movement_frame, text="← Left",
                  command=lambda: self.move("left"), **btn_cfg).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(movement_frame, text="Right →",
                  command=lambda: self.move("right"), **btn_cfg).grid(row=1, column=2, padx=3, pady=3)
        tk.Button(movement_frame, text="↓ Back",
                  command=lambda: self.move("backward"), **btn_cfg).grid(row=2, column=1, padx=3, pady=3)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=8)

        # Rotation
        tk.Button(right_frame, text="⟲ Rotate Left", command=lambda: self.rotate(-90),
                  width=18).pack(pady=3)
        tk.Button(right_frame, text="⟳ Rotate Right", command=lambda: self.rotate(90),
                  width=18).pack(pady=3)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=8)

        # Emergency
        tk.Button(right_frame, text="EMERGENCY STOP", command=self.emergency,
                  bg="red", fg="white", font=("Arial", 10, "bold"), width=18).pack(pady=5)

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