import pybullet as p
import pybullet_data
import numpy as np
import time
import tkinter as tk

# Define sensor directions and distances
sensor_directions = {
    "up": [0, 0, 1],
    "down": [0, 0, -1],
    "forward": [1, 0, 0],
    "backward": [-1, 0, 0],
    "right": [0, -1, 0],
    "left": [0, 1, 0]
}


# Function to calculate distance using ray casting
def calculate_distance(sensor_pos, sensor_dir, max_distance=10):
    ray_start = sensor_pos
    ray_end = np.add(sensor_pos, np.multiply(sensor_dir, max_distance))
    ray_info = p.rayTest(ray_start, ray_end)

    hit_object_id, hit_position = ray_info[0][0], ray_info[0][3]

    if hit_object_id != -1:
        distance = np.linalg.norm(np.subtract(hit_position, sensor_pos))
    else:
        distance = max_distance

    return distance


# Function to get sensor distances
def get_sensor_distances(drone_id):
    position, orientation = p.getBasePositionAndOrientation(drone_id)
    rotation_matrix = np.array(p.getMatrixFromQuaternion(orientation)).reshape(3, 3)

    distances = {}
    for key, direction in sensor_directions.items():
        world_direction = rotation_matrix.dot(direction)
        distances[key] = calculate_distance(position, world_direction)

    return distances


def move_drone(direction):
    global drone_pos
    if direction == "forward":
        drone_pos[0] += 0.1
    elif direction == "backward":
        drone_pos[0] -= 0.1
    elif direction == "left":
        drone_pos[1] += 0.1
    elif direction == "right":
        drone_pos[1] -= 0.1
    elif direction == "up":
        drone_pos[2] += 0.1
    elif direction == "down":
        drone_pos[2] -= 0.1

    p.resetBasePositionAndOrientation(drone_id, drone_pos, p.getQuaternionFromEuler([0, 0, 0]))


def main():
    global drone_id, drone_pos

    # Initialize PyBullet
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)

    # Load a plane and drone URDF
    plane_id = p.loadURDF("plane.urdf")
    drone_id = p.loadURDF("r2d2.urdf", basePosition=[0, 0, 1])
    drone_pos = [0, 0, 1]

    # Create some obstacles for the drone to sense
    p.loadURDF("block.urdf", basePosition=[2, 0, 1])  # Forward obstacle
    p.loadURDF("block.urdf", basePosition=[-2, 0, 1])  # Backward obstacle
    p.loadURDF("block.urdf", basePosition=[0, 2, 1])  # Left obstacle
    p.loadURDF("block.urdf", basePosition=[0, -2, 1])  # Right obstacle
    p.loadURDF("block.urdf", basePosition=[0, 0, 3])  # Up obstacle

    # Run the simulation in a separate thread
    def run_simulation():
        while True:
            p.stepSimulation()
            distances = get_sensor_distances(drone_id)
            print("Sensor distances:", distances)
            time.sleep(0.1)

    import threading
    sim_thread = threading.Thread(target=run_simulation)
    sim_thread.daemon = True
    sim_thread.start()

    # Create a simple GUI with buttons to control the drone
    root = tk.Tk()
    root.title("Drone Control")

    btn_forward = tk.Button(root, text="Forward", command=lambda: move_drone("forward"))
    btn_backward = tk.Button(root, text="Backward", command=lambda: move_drone("backward"))
    btn_left = tk.Button(root, text="Left", command=lambda: move_drone("left"))
    btn_right = tk.Button(root, text="Right", command=lambda: move_drone("right"))
    btn_up = tk.Button(root, text="Up", command=lambda: move_drone("up"))
    btn_down = tk.Button(root, text="Down", command=lambda: move_drone("down"))

    btn_forward.grid(row=0, column=1)
    btn_left.grid(row=1, column=0)
    btn_backward.grid(row=1, column=1)
    btn_right.grid(row=1, column=2)
    btn_up.grid(row=2, column=1)
    btn_down.grid(row=3, column=1)

    root.mainloop()

    p.disconnect()


if __name__ == "__main__":
    main()
