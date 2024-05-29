import pygame
import cv2
import networkx as nx
import random


def load_map(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary_map = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    return binary_map


def create_graph(binary_map, node_size):
    height, width = binary_map.shape
    G = nx.Graph()
    for y in range(0, height, node_size):
        for x in range(0, width, node_size):
            if binary_map[y, x] == 255:  # Open space pixel
                G.add_node((x, y))
                if x > 0 and binary_map[y, x - node_size] == 255:
                    G.add_edge((x, y), (x - node_size, y))
                if x < width - node_size and binary_map[y, x + node_size] == 255:
                    G.add_edge((x, y), (x + node_size, y))
                if y > 0 and binary_map[y - node_size, x] == 255:
                    G.add_edge((x, y), (x, y - node_size))
                if y < height - node_size and binary_map[y + node_size, x] == 255:
                    G.add_edge((x, y), (x, y + node_size))
    if not nx.is_connected(G):
        largest_cc = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest_cc).copy()
    return G


def draw_map(screen, binary_map, width, height):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    map_surface = pygame.Surface((width, height))
    for y in range(height):
        for x in range(width):
            if binary_map[y, x] == 0:  # Wall
                map_surface.set_at((x, y), BLACK)
            else:  # Open space
                map_surface.set_at((x, y), WHITE)
    return map_surface


def draw_drone(screen, pos, drone_radius):
    RED = (255, 0, 0)
    pygame.draw.circle(screen, RED, pos, drone_radius)


def detect_wall(pos, direction, binary_map, drone_radius, width, height):
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


def move_drone_dfs(pos, drone_step, visited, stack, binary_map, width, height, drone_radius):
    x, y = pos
    directions = ['left', 'right', 'up', 'down']
    random.shuffle(directions)  # Randomize direction priority

    for direction in directions:
        new_pos = None
        if direction == 'left' and (x - drone_step, y) not in visited and not detect_wall(pos, direction, binary_map,
                                                                                          drone_radius, width, height):
            new_pos = (x - drone_step, y)
        elif direction == 'right' and (x + drone_step, y) not in visited and not detect_wall(pos, direction, binary_map,
                                                                                             drone_radius, width,
                                                                                             height):
            new_pos = (x + drone_step, y)
        elif direction == 'up' and (x, y - drone_step) not in visited and not detect_wall(pos, direction, binary_map,
                                                                                          drone_radius, width, height):
            new_pos = (x, y - drone_step)
        elif direction == 'down' and (x, y + drone_step) not in visited and not detect_wall(pos, direction, binary_map,
                                                                                            drone_radius, width,
                                                                                            height):
            new_pos = (x, y + drone_step)

        if new_pos:
            visited.add(new_pos)
            stack.append(new_pos)
            return new_pos

    stack.pop()
    if stack:
        return stack[-1]
    return pos


def avoid_walls(pos, drone_step, binary_map, drone_radius, width, height):
    x, y = pos
    wall_directions = []

    if detect_wall(pos, 'left', binary_map, drone_radius, width, height):
        wall_directions.append('left')
    if detect_wall(pos, 'right', binary_map, drone_radius, width, height):
        wall_directions.append('right')
    if detect_wall(pos, 'up', binary_map, drone_radius, width, height):
        wall_directions.append('up')
    if detect_wall(pos, 'down', binary_map, drone_radius, width, height):
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

    return x, y


def get_sensor_readings(pos, binary_map, SENSOR_RANGE, SENSOR_ERROR, width, height):
    x, y = pos
    d_left = min(SENSOR_RANGE, sum(binary_map[y, max(0, x - i)] == 255 for i in range(SENSOR_RANGE))) * (
                1 + random.uniform(-SENSOR_ERROR, SENSOR_ERROR))
    d_right = min(SENSOR_RANGE, sum(binary_map[y, min(width - 1, x + i)] == 255 for i in range(SENSOR_RANGE))) * (
                1 + random.uniform(-SENSOR_ERROR, SENSOR_ERROR))
    d_up = min(SENSOR_RANGE, sum(binary_map[max(0, y - i), x] == 255 for i in range(SENSOR_RANGE))) * (
                1 + random.uniform(-SENSOR_ERROR, SENSOR_ERROR))
    d_down = min(SENSOR_RANGE, sum(binary_map[min(height - 1, y + i), x] == 255 for i in range(SENSOR_RANGE))) * (
                1 + random.uniform(-SENSOR_ERROR, SENSOR_ERROR))
    return [d_left, d_right, d_up, d_down]
