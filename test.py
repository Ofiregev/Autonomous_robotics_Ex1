import pygame
import numpy as np
from PIL import Image

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Path Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Define the drone
drone_radius = 10
drone_pos = np.array([70, 70])  # Adjusted starting position on a white path
drone_direction = np.array([1, 0])  # Initial direction (moving right)

# Load the map image and convert to binary map
map_image = Image.open('DroneSimulator-master/Maps/p11.png').convert('L')
binary_map = np.array(map_image)
binary_map[binary_map > 0] = 1  # Path
binary_map[binary_map == 0] = 0  # Walls

# Make the frame black to treat it as a wall
binary_map[0, :] = 0
binary_map[-1, :] = 0
binary_map[:, 0] = 0
binary_map[:, -1] = 0


def find_initial_position(binary_map):
    """Find the first white pixel in the binary map and return its coordinates."""
    for y in range(binary_map.shape[0]):
        for x in range(binary_map.shape[1]):
            if binary_map[y, x] == 1:
                return np.array([x, y])
    raise ValueError("No valid starting position found in the map.")


# Ensure initial position is on the path
if binary_map[int(drone_pos[1]), int(drone_pos[0])] == 0:
    raise ValueError("Initial position is on a wall. Please set it on a white path.")

# Sensor directions
sensor_directions = {
    "forward": [1, 0],
    "backward": [-1, 0],
    "right": [0, 1],
    "left": [0, -1]
}

# Set shorter sensor range
sensor_range = 20


def calculate_distance(drone_pos, direction, max_distance=sensor_range):
    """Calculate distance from the drone to the nearest wall in the given direction."""
    min_distance = max_distance
    for d in range(1, max_distance + 1):
        check_pos = drone_pos + np.array(direction) * d
        x, y = int(check_pos[0]), int(check_pos[1])

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT or binary_map[y, x] == 0:
            min_distance = d - 1
            break
    return min_distance


def draw_environment():
    """Draw the environment including walls and the drone."""
    screen.fill(WHITE)

    # Draw the map
    for y in range(binary_map.shape[0]):
        for x in range(binary_map.shape[1]):
            color = WHITE if binary_map[y, x] == 1 else BLACK
            screen.set_at((x, y), color)

    # Draw drone
    pygame.draw.circle(screen, RED, drone_pos.astype(int), drone_radius)

    # Draw sensor rays
    for direction in sensor_directions.values():
        end_pos = drone_pos + np.array(direction) * calculate_distance(drone_pos, direction)
        pygame.draw.line(screen, RED, drone_pos, end_pos, 1)

    pygame.display.flip()


def get_sensor_distances(drone_pos):
    """Get sensor distances for the drone."""
    distances = {}
    for key, direction in sensor_directions.items():
        distances[key] = calculate_distance(drone_pos, direction)
    return distances


# Path memory to avoid cycles
path_memory = []


def move_drone(sensor_data):
    """Move the drone based on sensor data to avoid walls and prevent cycles."""
    global drone_pos, drone_direction
    step_size = 8  # Increase step size for faster movement
    min_distance = 10  # Minimum distance to maintain from walls
    path_memory_size = 10  # Size of the path memory to detect cycles

    # Priority order for directions: forward, right, down, left, backward
    priority_directions = ["forward", "right", "left", "backward"]

    for direction in priority_directions:
        if sensor_data[direction] >= min_distance:
            drone_direction = np.array(sensor_directions[direction])
            new_pos = drone_pos + drone_direction * step_size

            # Check if the new position is valid and not in path memory
            if (0 <= new_pos[0] < WIDTH and 0 <= new_pos[1] < HEIGHT and
                    binary_map[int(new_pos[1]), int(new_pos[0])] == 1 and
                    tuple(new_pos) not in path_memory):

                # Update path memory
                path_memory.append(tuple(drone_pos))
                if len(path_memory) > path_memory_size:
                    path_memory.pop(0)

                drone_pos = new_pos
                return


# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update environment
    draw_environment()

    # Get sensor distances
    distances = get_sensor_distances(drone_pos)
    print("Sensor distances:", distances)

    # Move the drone based on sensor distances
    move_drone(distances)

    clock.tick(60)

pygame.quit()
