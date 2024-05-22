import tkinter as tk
from tkinter import ttk
import pybullet as p
import pybullet_data
import time
from threading import Event

from AutoAlgo1 import AutoAlgo1
from CPU import CPU
from Painter import Painter


class SimulationWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Simulator")
        self.root.geometry("1800x700")
        self.toogle_stop = True

        # PyBullet setup
        self.physicsClient = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        self.planeId = p.loadURDF("plane.urdf")
        self.boxId = p.loadURDF("r2d2.urdf", [0, 0, 1])
        p.setGravity(0, 0, -9.8)

        # Algorithm and painter
        self.map = "p11.png"  # Provide a valid path
        self.algo1 = AutoAlgo1(self.map)
        self.painter = Painter(self.root, self.algo1)
        self.painter.place(x=0, y=0, width=1200, height=700)

        # Create buttons
        self.create_buttons()

        # Info label
        self.info_label = ttk.Label(root, text="", wraplength=300)
        self.info_label.place(x=1300, y=500, width=300, height=200)

        self.update_info()

        # CPUs
        self.painter_cpu = CPU(60, "painter")  # 60 FPS painter
        self.painter_cpu.add_function(self.painter.draw)
        self.painter_cpu.play()

        self.updates_cpu = CPU(60, "updates")
        self.updates_cpu.add_function(self.algo1.update)
        self.updates_cpu.play()

        self.info_cpu = CPU(6, "update_info")
        self.info_cpu.add_function(self.update_info)
        self.info_cpu.play()

        # Run simulation in main thread using Tkinter's after method
        self.simulation_running = True
        self.run_simulation()

    def create_buttons(self):
        # Start/Pause button
        self.stop_btn = ttk.Button(self.root, text="Start/Pause", command=self.toggle_simulation)
        self.stop_btn.place(x=1300, y=0, width=170, height=50)

        # Speed Up button
        self.speed_up_btn = ttk.Button(self.root, text="Speed Up", command=self.algo1.speed_up)
        self.speed_up_btn.place(x=1300, y=100, width=100, height=50)

        # Speed Down button
        self.speed_down_btn = ttk.Button(self.root, text="Speed Down", command=self.algo1.speed_down)
        self.speed_down_btn.place(x=1400, y=100, width=100, height=50)

        # Spin buttons
        self.create_spin_buttons()

        # Toggle Map button
        self.toogle_map_btn = ttk.Button(self.root, text="Toggle Map", command=self.toggle_map)
        self.toogle_map_btn.place(x=1300, y=400, width=120, height=50)

        # Toggle AI button
        self.toogle_ai_btn = ttk.Button(self.root, text="Toggle AI", command=self.toggle_ai)
        self.toogle_ai_btn.place(x=1400, y=400, width=120, height=50)

        # Return Home button
        self.return_btn = ttk.Button(self.root, text="Return Home", command=self.return_home)
        self.return_btn.place(x=1500, y=400, width=120, height=50)

        # Open Graph button
        self.graph_btn = ttk.Button(self.root, text="Open Graph", command=self.open_graph)
        self.graph_btn.place(x=1600, y=400, width=120, height=50)

    def create_spin_buttons(self):
        spin_angles = [180, 90, 60, 45, 30, -30, -45, -60]
        x_positions = [1300, 1400, 1500, 1300, 1400, 1500, 1600, 1700]
        y_position = 200

        for i, angle in enumerate(spin_angles):
            btn = ttk.Button(self.root, text=f"Spin {angle}", command=lambda a=angle: self.algo1.spin_by(a))
            btn.place(x=x_positions[i], y=y_position, width=100, height=50)
            if i == 3:
                y_position += 100

    def run_simulation(self):
        if self.simulation_running:
            p.stepSimulation()
            self.root.after(4, self.run_simulation)  # Run simulation step every 4 ms (approx. 240 Hz)

    def toggle_simulation(self):
        self.simulation_running = not self.simulation_running
        if self.simulation_running:
            self.run_simulation()

    def toggle_map(self):
        print("Toggle map action triggered")

    def toggle_ai(self):
        print("Toggle AI action triggered")

    def return_home(self):
        print("Return home action triggered")

    def open_graph(self):
        print("Open graph action triggered")

    def update_info(self):
        self.info_label.config(text=self.algo1.get_info_html())
        self.root.after(1000, self.update_info)

    def on_closing(self):
        self.simulation_running = False
        CPU.stop_all_cpus()
        self.root.destroy()
        p.disconnect()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
