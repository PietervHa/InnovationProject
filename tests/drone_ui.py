import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import cv2
import threading
import time
import numpy as np

from src.drone_controller import DroneController


# ==============================
# AUTO FLIGHT ROUTES
# ==============================

ROUTES = {
    "Basic Route": [
        ("takeoff", None),
        ("move", ("forward", 50)),
        ("rotate", 90),
        ("move", ("right", 30)),
        ("move", ("backward", 40)),
        ("land", None),
    ],
    "Demo Route": [
        ("takeoff", None),
        ("move", ("forward", 40)),
        ("rotate", 90),
        ("move", ("left", 30)),
        ("rotate", -90),
        ("move", ("backward", 40)),
        ("land", None),
    ],
    "Square Route": [
        ("takeoff", None),
        ("move", ("forward", 50)),
        ("rotate", 90),
        ("move", ("forward", 50)),
        ("rotate", 90),
        ("move", ("forward", 50)),
        ("rotate", 90),
        ("move", ("forward", 50)),
        ("land", None),
    ],
    "Hover & Spin": [
        ("takeoff", None),
        ("move", ("up", 30)),
        ("rotate", 90),
        ("rotate", 90),
        ("rotate", 90),
        ("rotate", 90),
        ("move", ("down", 20)),
        ("land", None),
    ],
}


class DroneUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tello Drone Controller")
        self.root.geometry("900x600")

        self.drone = DroneController()
        self.connected = False
        self.video_running = False
        self.route_running = False

        # Prevents two commands from running at the same time
        self.command_lock = threading.Lock()

        # Latest frame storage
        self.latest_frame = None
        self.frame_lock = threading.Lock()

        # Pre-built blank frame shown before drone connects
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        self._imgtk = ImageTk.PhotoImage(image=Image.fromarray(blank))

        # ===== MAIN LAYOUT =====
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== LEFT: VIDEO FEED =====
        left_frame = tk.Frame(main_frame, bg="black", width=640, height=480)
        left_frame.pack(side="left", fill="both", expand=True)
        left_frame.pack_propagate(False)

        self.video_label = tk.Label(left_frame, bg="black", image=self._imgtk)
        self.video_label.pack(expand=True)

        # ===== RIGHT: CONTROLS =====
        right_frame = tk.Frame(main_frame, padx=10)
        right_frame.pack(side="right", fill="y")

        self.battery_label = tk.Label(right_frame, text="Battery: --%", font=("Arial", 13))
        self.battery_label.pack(pady=(0, 5))

        # Status label shows when a command is in progress
        self.status_label = tk.Label(right_frame, text="", font=("Arial", 9), fg="gray")
        self.status_label.pack()

        tk.Button(right_frame, text="Connect Drone", command=self.connect_drone,
                  bg="lightblue", width=18).pack(pady=5)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=8)

        tk.Button(right_frame, text="Takeoff", command=self.takeoff,
                  bg="lightgreen", width=18).pack(pady=3)
        tk.Button(right_frame, text="Land", command=self.land,
                  bg="orange", width=18).pack(pady=3)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=8)

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

        tk.Button(right_frame, text="⟲ Rotate Left", command=lambda: self.rotate(-90),
                  width=18).pack(pady=3)
        tk.Button(right_frame, text="⟳ Rotate Right", command=lambda: self.rotate(90),
                  width=18).pack(pady=3)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=8)

        # ===== AUTO FLIGHT ROUTES =====
        tk.Label(right_frame, text="Auto Flight Routes", font=("Arial", 10, "bold")).pack(pady=(0, 4))

        self.route_var = tk.StringVar(value=list(ROUTES.keys())[0])
        route_menu = ttk.Combobox(
            right_frame,
            textvariable=self.route_var,
            values=list(ROUTES.keys()),
            state="readonly",
            width=16,
        )
        route_menu.pack(pady=3)

        self.fly_route_btn = tk.Button(
            right_frame,
            text="▶ Fly Route",
            command=self.fly_selected_route,
            bg="#7EC8E3",
            width=18,
        )
        self.fly_route_btn.pack(pady=3)

        self.stop_route_btn = tk.Button(
            right_frame,
            text="■ Stop Route",
            command=self.stop_route,
            bg="#FFD580",
            width=18,
            state="disabled",
        )
        self.stop_route_btn.pack(pady=3)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=8)

        # Emergency bypasses the command lock entirely — always fires immediately
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

            threading.Thread(target=self.video_capture_loop, daemon=True).start()
            threading.Thread(target=self.update_battery, daemon=True).start()
            self.root.after(15, self.render_frame)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_command(self, label, fn, *args):
        """
        Runs any drone command in a background thread.
        Skips if a command is already running (non-blocking tryacquire).
        Shows a status label while the command is in flight.
        """
        if not self.connected:
            return

        # tryacquire: if lock is taken, skip this command instead of queuing
        if not self.command_lock.acquire(blocking=False):
            self.set_status("Busy...")
            return

        def task():
            try:
                self.set_status(f"{label}...")
                fn(*args)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Command Error", str(e)))
            finally:
                self.command_lock.release()
                self.set_status("")

        threading.Thread(target=task, daemon=True).start()

    def set_status(self, text):
        """Thread-safe status label update."""
        self.root.after(0, lambda: self.status_label.config(text=text))

    def update_battery(self):
        while self.connected:
            try:
                battery = self.drone.get_battery()
                self.root.after(0, lambda b=battery: self.battery_label.config(text=f"Battery: {b}%"))
            except Exception:
                pass
            time.sleep(5)

    def video_capture_loop(self):
        """Background thread: grabs and pre-processes frames as fast as possible."""
        while self.video_running:
            try:
                frame = self.drone.get_frame()
                if frame is None:
                    continue

                frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_NEAREST)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                with self.frame_lock:
                    self.latest_frame = frame

            except Exception:
                pass

    def render_frame(self):
        """Main thread: renders the latest pre-processed frame."""
        if self.video_running:
            with self.frame_lock:
                frame = self.latest_frame

            if frame is not None:
                img = Image.fromarray(frame)
                self._imgtk.paste(img)
                self.video_label.configure(image=self._imgtk)

            self.root.after(15, self.render_frame)

    # ===== AUTO FLIGHT ROUTE EXECUTION =====

    def fly_selected_route(self):
        """Start the selected auto flight route in a background thread."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Connect the drone first.")
            return
        if self.route_running:
            self.set_status("Route already running...")
            return

        route_name = self.route_var.get()
        steps = ROUTES.get(route_name, [])

        self.route_running = True
        self.root.after(0, lambda: self.fly_route_btn.config(state="disabled"))
        self.root.after(0, lambda: self.stop_route_btn.config(state="normal"))

        threading.Thread(target=self._execute_route, args=(route_name, steps), daemon=True).start()

    def _execute_route(self, route_name, steps):
        """Background thread: executes each step of the route sequentially."""
        try:
            self.set_status(f"Route: {route_name} — starting…")
            time.sleep(0.5)

            for i, step in enumerate(steps):
                if not self.route_running:
                    self.set_status("Route stopped.")
                    return

                action, value = step
                step_label = self._step_label(action, value)
                self.set_status(f"[{i + 1}/{len(steps)}] {step_label}")

                # Acquire the shared command lock so manual buttons are blocked during route
                self.command_lock.acquire()
                try:
                    if action == "takeoff":
                        self.drone.takeoff()
                    elif action == "land":
                        self.drone.land()
                    elif action == "move":
                        direction, distance = value
                        self.drone.move(direction, distance)
                    elif action == "rotate":
                        self.drone.rotate(value)
                finally:
                    self.command_lock.release()

                # Pause between steps — bail early if route was stopped
                for _ in range(20):
                    if not self.route_running:
                        return
                    time.sleep(0.1)

            self.set_status(f"Route '{route_name}' complete!")

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Route Error", str(e)))
        finally:
            self.route_running = False
            self.root.after(0, lambda: self.fly_route_btn.config(state="normal"))
            self.root.after(0, lambda: self.stop_route_btn.config(state="disabled"))

    def stop_route(self):
        """Interrupt the running route after the current step finishes."""
        self.route_running = False
        self.set_status("Stopping route…")

    @staticmethod
    def _step_label(action, value):
        """Human-readable label for a route step."""
        if action == "takeoff":
            return "Takeoff"
        if action == "land":
            return "Land"
        if action == "move":
            direction, distance = value
            return f"Move {direction} {distance} cm"
        if action == "rotate":
            direction = "clockwise" if value > 0 else "counter-clockwise"
            return f"Rotate {abs(value)}° {direction}"
        return action

    # ===== DRONE COMMANDS — all routed through run_command =====

    def takeoff(self):
        self.run_command("Takeoff", self.drone.takeoff)

    def land(self):
        self.run_command("Landing", self.drone.land)

    def move(self, direction):
        self.run_command(f"Moving {direction}", self.drone.move, direction, 30)

    def rotate(self, angle):
        label = "Rotating left" if angle < 0 else "Rotating right"
        self.run_command(label, self.drone.rotate, angle)

    def emergency(self):
        # Skips the lock — emergency must always fire instantly
        self.route_running = False  # also abort any running route
        threading.Thread(target=self.drone.emergency_stop, daemon=True).start()
        self.set_status("EMERGENCY STOP")


if __name__ == "__main__":
    root = tk.Tk()
    app = DroneUI(root)
    root.mainloop()