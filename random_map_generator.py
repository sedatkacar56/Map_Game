import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import random

# Real world country names pool
COUNTRY_NAMES_POOL = [
    "USA", "China", "Russia", "Germany", "France", "UK", "Japan", "India",
    "Brazil", "Canada", "Italy", "Spain", "Turkey", "Mexico", "South Korea",
    "Australia", "Netherlands", "Saudi Arabia", "Switzerland", "Sweden",
    "Poland", "Belgium", "Thailand", "Austria", "Norway", "Egypt", "Argentina",
    "South Africa", "Pakistan", "Vietnam", "Bangladesh", "Iran", "Ukraine"
]

def generate_random_color():
    """Generate a random RGB color"""
    return (random.random(), random.random(), random.random())

def create_random_map(num_countries=10, min_cells_per_country=10):
    """
    Create a random rectangular map with specified number of countries
    Each country gets at least min_cells_per_country cells
    """
    # Calculate grid size
    total_cells = num_countries * min_cells_per_country
    
    # Make it roughly square/rectangle
    grid_height = int(np.sqrt(total_cells))
    grid_width = int(np.ceil(total_cells / grid_height))
    
    # Make sure we have enough cells
    while grid_height * grid_width < total_cells:
        grid_width += 1
    
    # Create empty map
    map_data = np.zeros((grid_height, grid_width), dtype=int)
    
    # Select random country names
    selected_names = random.sample(COUNTRY_NAMES_POOL, min(num_countries, len(COUNTRY_NAMES_POOL)))
    country_names = {i+1: selected_names[i] for i in range(len(selected_names))}
    
    # Generate random colors for each country
    country_colors = {i+1: generate_random_color() for i in range(num_countries)}
    
    # Place initial seeds for each country randomly
    seeds = []
    for country_id in range(1, num_countries + 1):
        while True:
            x = random.randint(0, grid_height - 1)
            y = random.randint(0, grid_width - 1)
            if map_data[x, y] == 0:  # Empty cell
                map_data[x, y] = country_id
                seeds.append((country_id, x, y))
                break
    
    # Grow each country to minimum size
    for country_id in range(1, num_countries + 1):
        current_size = np.sum(map_data == country_id)
        
        while current_size < min_cells_per_country:
            # Get all cells of this country
            country_cells = np.argwhere(map_data == country_id)
            
            # Find empty neighbors
            empty_neighbors = []
            for x, y in country_cells:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < grid_height and 0 <= ny < grid_width and 
                        map_data[nx, ny] == 0):
                        empty_neighbors.append((nx, ny))
            
            if empty_neighbors:
                # Pick random empty neighbor and claim it
                nx, ny = random.choice(empty_neighbors)
                map_data[nx, ny] = country_id
                current_size += 1
            else:
                # No empty neighbors, try to find any empty cell nearby
                found = False
                for x, y in country_cells:
                    for radius in range(1, 5):
                        for dx in range(-radius, radius + 1):
                            for dy in range(-radius, radius + 1):
                                nx, ny = x + dx, y + dy
                                if (0 <= nx < grid_height and 0 <= ny < grid_width and 
                                    map_data[nx, ny] == 0):
                                    map_data[nx, ny] = country_id
                                    current_size += 1
                                    found = True
                                    break
                            if found:
                                break
                        if found:
                            break
                    if found:
                        break
                
                if not found:
                    break
    
    # Fill remaining empty cells with nearest country
    empty_cells = np.argwhere(map_data == 0)
    for x, y in empty_cells:
        # Find nearest non-zero cell
        min_dist = float('inf')
        nearest_country = 1
        
        for i in range(grid_height):
            for j in range(grid_width):
                if map_data[i, j] != 0:
                    dist = abs(i - x) + abs(j - y)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_country = map_data[i, j]
        
        map_data[x, y] = nearest_country
    
    return map_data, country_names, country_colors

def draw_map(map_data, country_colors, country_names, show_names=True):
    """Draw the map with country names"""
    fig, ax = plt.subplots(figsize=(12, 12))
    
    unique_ids = np.unique(map_data)
    max_id = max(unique_ids)
    colors = [country_colors.get(i, (0, 0, 0)) for i in range(max_id + 1)]
    cmap = ListedColormap(colors)
    
    ax.imshow(map_data, cmap=cmap, interpolation='nearest')
    ax.axis('off')
    
    # Add country names
    if show_names:
        country_positions = {}
        grid_height, grid_width = map_data.shape
        
        for i in range(grid_height):
            for j in range(grid_width):
                country_id = map_data[i, j]
                if country_id not in country_positions:
                    country_positions[country_id] = []
                country_positions[country_id].append((j, i))
        
        for country_id, positions in country_positions.items():
            if country_id in country_names and len(positions) > 2:
                avg_x = sum(x for x, y in positions) / len(positions)
                avg_y = sum(y for x, y in positions) / len(positions)
                ax.text(avg_x, avg_y, country_names[country_id],
                       ha="center", va="center", fontsize=9, 
                       color="white", weight="bold",
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.7))
    
    return fig

