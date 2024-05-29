import pygame
import sys
import random
import time
import drone_simulation as ds

# Load the map image
image_path = sys.argv[1]
binary_map = ds.load_map(image_path)

# Get the dimensions of the binary map
height, width = binary_map.shape

# Define the size of each node in the grid
node_size = 10

# Create a graph
G = ds.create_graph(binary_map, node_size)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drone Simulation")

# Draw the map
map_surface = ds.draw_map(screen, binary_map, width, height)

# Drone properties
drone_pos = random.choice(list(G.nodes()))
drone_radius = 10
drone_step = node_size  # Move by node_size
battery = 480  # 8 minutes in seconds

# Track visited nodes
visited = set()
visited.add(drone_pos)

# DFS stack
stack = [drone_pos]

# Initialize sensor properties
SENSOR_RANGE = 300  # in pixels (3 meters)
SENSOR_ERROR = 0.02  # 2% error
UPDATE_RATE = 10  # Hz

clock = pygame.time.Clock()
running = True
start_time = time.time()

# Initialize a flag for backtracking
backtracking = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(map_surface, (0, 0))
    ds.draw_drone(screen, drone_pos, drone_radius)

    if not stack:
        break

    new_pos = ds.move_drone_dfs(drone_pos, drone_step, visited, stack, binary_map, width, height, drone_radius)
    if ds.detect_wall(new_pos, 'left', binary_map, drone_radius, width, height) or ds.detect_wall(new_pos, 'right', binary_map, drone_radius, width, height) or ds.detect_wall(new_pos, 'up', binary_map, drone_radius, width, height) or ds.detect_wall(new_pos, 'down', binary_map, drone_radius, width, height):
        new_pos = ds.avoid_walls(new_pos, drone_step, binary_map, drone_radius, width, height)
    drone_pos = new_pos

    sensor_readings = ds.get_sensor_readings(drone_pos, binary_map, SENSOR_RANGE, SENSOR_ERROR, width, height)
    d_left, d_right, d_up, d_down = sensor_readings
    print(f"Sensor readings (in pixels): Left: {d_left:.2f}, Right: {d_right:.2f}, Up: {d_up:.2f}, Down: {d_down:.2f}")

    elapsed_time = time.time() - start_time
    battery_remaining = max(0, int(battery - elapsed_time))
    if battery_remaining <= battery / 2:  # When battery reaches 50%
        print("Battery level is at 50%. Backtracking to starting point...")
        backtracking = True
        for i in range(len(stack) - 2, -1, -1):
            if ds.detect_wall(stack[i], 'left', binary_map, drone_radius, width, height) or ds.detect_wall(stack[i], 'right', binary_map, drone_radius, width, height) or ds.detect_wall(stack[i], 'up', binary_map, drone_radius, width, height) or ds.detect_wall(stack[i], 'down', binary_map, drone_radius, width, height):
                continue
            drone_pos = stack[i]
            stack = stack[:i + 1]
            break
    elif battery_remaining == 0:
        print("Battery empty. Landing...")
        running = False
    else:
        print(f"Battery remaining: {battery_remaining:.2f} seconds")
        backtracking = False

    pygame.display.flip()
    clock.tick(UPDATE_RATE)

pygame.quit()
