import threading
import pygame
import cv2
import networkx as nx
import random
import time

# Load the map image
image_path = 'p11.png'  # Replace with your image path
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Threshold the image to create a binary map (0 for walls, 255 for open space)
_, binary_map = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)

# Get the dimensions of the binary map
height, width = binary_map.shape

# Define the size of each node in the grid
node_size = 10

# Create a graph
G = nx.Graph()

# Iterate through the binary map with a step size of node_size
for y in range(0, height, node_size):
    for x in range(0, width, node_size):
        if binary_map[y, x] == 255:  # Open space pixel
            G.add_node((x, y))
            # Connect to adjacent nodes (4-connectivity: up, down, left, right)
            if x > 0 and binary_map[y, x - node_size] == 255:
                G.add_edge((x, y), (x - node_size, y))
            if x < width - node_size and binary_map[y, x + node_size] == 255:
                G.add_edge((x, y), (x + node_size, y))
            if y > 0 and binary_map[y - node_size, x] == 255:
                G.add_edge((x, y), (x, y - node_size))
            if y < height - node_size and binary_map[y + node_size, x] == 255:
                G.add_edge((x, y), (x, y + node_size))

# Ensure the graph is connected
if not nx.is_connected(G):
    largest_cc = max(nx.connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drone Simulation")
pygame.display.set_icon(pygame.image.load('./src/drone.png'))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Font
font = pygame.font.SysFont(None, 24)

# Draw the map
map_surface = pygame.Surface((width, height))
for y in range(height):
    for x in range(width):
        if binary_map[y, x] == 0:  # Wall
            map_surface.set_at((x, y), BLACK)
        else:  # Open space
            map_surface.set_at((x, y), WHITE)

# Drone properties
drone_pos = random.choice(list(G.nodes()))
drone_radius = 10  # Increase the radius of the drone
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

# Desired distance from obstacles
desired_distance = 100  # 100 pixels (1 meter)

# Define a lock for accessing shared resources
lock = threading.Lock()


# Function to draw the drone
def draw_drone(pos):
    pygame.draw.circle(screen, RED, pos, drone_radius)

# Function to detect walls
def detect_wall(pos, direction):
    x, y = pos
    if direction == 'left':
        for dx in range(1, drone_radius + 1):
            if (x - dx) < 0 or binary_map[y, x - dx] == 0:
                return True
    elif direction == 'right':
        for dx in range(1, drone_radius + 1):
            if (x + dx) >= width or binary_map[y, x + dx] == 0:
                return True
    elif direction == 'up':
        for dy in range(1, drone_radius + 1):
            if (y - dy) < 0 or binary_map[y - dy, x] == 0:
                return True
    elif direction == 'down':
        for dy in range(1, drone_radius + 1):
            if (y + dy) >= height or binary_map[y + dy, x] == 0:
                return True
    return False

# Function to move the drone with DFS-based exploration
def move_drone_dfs(pos):
    x, y = pos
    directions = ['left', 'right', 'up', 'down']
    random.shuffle(directions)  # Randomize direction priority

    for direction in directions:
        new_pos = None
        if direction == 'left' and (x - drone_step, y) not in visited and not detect_wall(pos, direction):
            new_pos = (x - drone_step, y)
        elif direction == 'right' and (x + drone_step, y) not in visited and not detect_wall(pos, direction):
            new_pos = (x + drone_step, y)
        elif direction == 'up' and (x, y - drone_step) not in visited and not detect_wall(pos, direction):
            new_pos = (x, y - drone_step)
        elif direction == 'down' and (x, y + drone_step) not in visited and not detect_wall(pos, direction):
            new_pos = (x, y + drone_step)

        if new_pos:
            with lock:
                visited.add(new_pos)
                stack.append(new_pos)
            return new_pos

    # If all directions are blocked or visited, backtrack
    with lock:
        stack.pop()
    if stack:
        return stack[-1]
    return pos

# Function to avoid walls
def avoid_walls(pos):
    x, y = pos
    wall_directions = []

    if detect_wall(pos, 'left'):
        wall_directions.append('left')
    if detect_wall(pos, 'right'):
        wall_directions.append('right')
    if detect_wall(pos, 'up'):
        wall_directions.append('up')
    if detect_wall(pos, 'down'):
        wall_directions.append('down')

    if wall_directions:
        if 'left' in wall_directions:
            x += drone_step
        if 'right' in wall_directions:
            x -= drone_step
        if 'up' in wall_directions:
            y += drone_step
        if 'down' in wall_directions:
            y -= drone_step

    return (x, y)

# Function to get sensor readings
def get_sensor_readings(pos):
    x, y = pos
    d_left = min(SENSOR_RANGE, sum(binary_map[y, max(0, x - i)] == 255 for i in range(SENSOR_RANGE))) * (
                1 + random.uniform(-SENSOR_ERROR, SENSOR_ERROR))
    d_right = min(SENSOR_RANGE, sum(binary_map[y, min(width - 1, x + i)] == 255 for i in range(SENSOR_RANGE))) * (
                1 + random.uniform(-SENSOR_ERROR, SENSOR_ERROR))
    d_up = min(SENSOR_RANGE, sum(binary_map[max(0, y - i), x] == 255 for i in range(SENSOR_RANGE))) * (1 + random.uniform(-SENSOR_ERROR, SENSOR_ERROR))
    d_down = min(SENSOR_RANGE, sum(binary_map[min(height - 1, y + i), x] == 255 for i in range(SENSOR_RANGE))) * (
                1 + random.uniform(-SENSOR_ERROR, SENSOR_ERROR))
    return [d_left, d_right, d_up, d_down]

# Function to calculate reward
def reward_function(sensor_readings, desired_distance):
    d_left, d_right, d_up, d_down = sensor_readings

    # Calculate the error based on sensor readings
    error = abs(desired_distance - min(d_left, d_right, d_up, d_down))

    # Define a reward function
    reward = 1 / (1 + error)  # Higher reward for smaller error

    return reward

# Function to move the drone
def move_drone():
    global drone_pos, stack
    if not stack:
        return
    new_pos = move_drone_dfs(drone_pos)
    if detect_wall(new_pos, 'left') or detect_wall(new_pos, 'right') or detect_wall(new_pos, 'up') or detect_wall(
            new_pos, 'down'):
        new_pos = avoid_walls(new_pos)
    drone_pos = new_pos

# Main loop
clock = pygame.time.Clock()
running = True
start_time = time.time()
backtracking = False  # Initialize a flag for backtracking

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(map_surface, (0, 0))

    draw_drone(drone_pos)

    # Move the drone
    move_drone()

    # Get sensor readings
    sensor_readings = get_sensor_readings(drone_pos)
    d_left, d_right, d_up, d_down = sensor_readings
    print(f"Sensor readings (in pixels): Left: {d_left:.2f}, Right: {d_right:.2f}, Up: {d_up:.2f}, Down: {d_down:.2f}")

    # Calculate reward
    reward = reward_function(sensor_readings, desired_distance)
    print(f"Reward: {reward:.2f}")

    # Check battery status
    elapsed_time = time.time() - start_time
    battery_remaining = max(0, battery - elapsed_time)
    if battery_remaining <= battery / 2:  # When battery reaches 50%
        print("Battery level is at 50%. Backtracking to starting point...")
        backtracking = True  # Set backtracking flag to True
        # Reverse DFS over the visited nodes list
        for i in range(len(stack) - 2, -1, -1):
            if detect_wall(stack[i], 'left') or detect_wall(stack[i], 'right') or detect_wall(stack[i], 'up') or detect_wall(
                    stack[i], 'down'):
                continue  # Skip nodes that are blocked by walls
            drone_pos = stack[i]  # Set drone position to the node
            stack = stack[:i + 1]  # Remove nodes after this node in the stack
            break
    elif battery_remaining == 0:
        print("Battery empty. Landing...")
        running = False
    else:
        print(f"Battery remaining: {battery_remaining:.2f} seconds")
        backtracking = False  # Reset backtracking flag when not backtracking

    # Display sensor readings, reward, and battery remaining
    text = f"Sensor readings: Left: {d_left:.2f}, Right: {d_right:.2f}, Up: {d_up:.2f}, Down: {d_down:.2f} | Reward: {reward:.2f} | Battery remaining: {battery_remaining:.2f} seconds"
    text_surface = font.render(text, True, RED)
    screen.blit(text_surface, (25, 15))

    pygame.display.flip()
    clock.tick(UPDATE_RATE)

pygame.quit()