# Autonomous_robotics_Ex1

# Drone Simulation

This project simulates a drone exploring a map using a depth-first search (DFS) algorithm. The drone navigates through open spaces while avoiding walls, gathering sensor data, and returning to the starting point if the battery level gets low. The simulation is visualized using Pygame.

## Requirements

- Python 3.x
- `pygame`
- `numpy`
- `opencv-python`
- `networkx`

## Installation

1. Clone the repository to your local machine:

    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Ensure you have your map image ready. The image should be in grayscale, with white representing open spaces and black representing walls.

2. Run the simulation:

    ```sh
    python solution.py <name_of_the_map>
    ```

    Replace `<name_of_the_map>` with the path to your map image file (e.g., `maps/p11.png`).

## Project Structure

- `solution.py`: The main script to run the simulation.
- `requirements.txt`: List of dependencies.

## Example

If you have a map image named `p11.png` in the `maps` directory, you would run:

```sh
python run.py maps/p11.png
