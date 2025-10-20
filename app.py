import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import random
from random_map_generator import create_random_map, COUNTRY_NAMES_POOL

# Page config
st.set_page_config(page_title="Map Game", page_icon="🗺️", layout="wide")

# Initialize session state
if 'map_data' not in st.session_state:
    st.session_state.map_data = None
    st.session_state.countries = {}
    st.session_state.country_names = {}
    st.session_state.country_colors = {}
    st.session_state.turn_count = 0
    st.session_state.stable_countries = set()

# Predefined map data
PREDEFINED_MAP = np.array([
    [0, 0, 0, 0, 1, 1, 2, 2, 2, 2],
    [0, 0, 0, 1, 1, 1, 2, 2, 2, 2],
    [0, 0, 1, 1, 1, 1, 2, 7, 7, 2],
    [3, 0, 3, 4, 4, 4, 4, 7, 7, 7],
    [3, 3, 3, 4, 4, 4, 7, 7, 7, 7],
    [3, 3, 3, 4, 4, 4, 4, 4, 4, 7],
    [5, 5, 5, 5, 4, 4, 4, 4, 4, 6],
    [5, 5, 5, 5, 5, 5, 4, 4, 6, 6],
    [5, 5, 5, 5, 5, 5, 6, 6, 6, 6],
    [5, 5, 5, 5, 5, 6, 6, 6, 6, 6],
])

PREDEFINED_NAMES = {
    0: "UU EMPIRE",
    1: "YELIZ EMPIRE",
    2: "STATE of SEDAT",
    3: "UNITED KINGDOM",
    4: "OTTOMANS",
    5: "USA",
    6: "GERMAN EMPIRE",
    7: "USSR"
}

PREDEFINED_COLORS = {
    0: (0, 0, 1),      # blue
    1: (0, 1, 0),      # green
    2: (1, 0, 0),      # red
    3: (1, 1, 0),      # yellow
    4: (0.5, 0, 0.5),  # purple
    5: (0.5, 0.5, 0.5),# grey
    6: (1, 0.75, 0.8), # pink
    7: (1, 0.65, 0)    # orange
}

def initialize_predefined_map():
    map_data = PREDEFINED_MAP.copy()
    countries = {}
    
    # Build countries dictionary
    for country_id in np.unique(map_data):
        if True:
            countries[country_id] = list(zip(*np.where(map_data == country_id)))
    
    return map_data, countries, PREDEFINED_NAMES.copy(), PREDEFINED_COLORS.copy()

def get_neighbors(x, y, grid_size):
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            neighbors.append((nx, ny))
    return neighbors

def invade(map_data, attacker, defender):
    grid_size = map_data.shape[0]
    attacker_cells = np.argwhere(map_data == attacker)
    
    for x, y in attacker_cells:
        for nx, ny in get_neighbors(x, y, grid_size):
            if map_data[nx, ny] == defender:
                map_data[nx, ny] = attacker
    
    return not np.any(map_data == defender)

def random_turn(map_data, stable_countries, countries):
    active_countries = [c for c in countries.keys() if c not in stable_countries]
    
    if len(active_countries) < 2:
        return False, None, None
    
    attacker = random.choice(active_countries)
    attacker_cells = np.argwhere(map_data == attacker)
    
    neighbors = set()
    for x, y in attacker_cells:
        for nx, ny in get_neighbors(x, y, map_data.shape[0]):
            neighbor_id = map_data[nx, ny]
            if neighbor_id != attacker and neighbor_id not in stable_countries:
                neighbors.add(neighbor_id)
    
    if not neighbors:
        return False, None, None
    
    defender = random.choice(list(neighbors))
    invade(map_data, attacker, defender)
    
    return True, attacker, defender

def draw_map(map_data, country_colors, country_names, show_names=True):
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
        grid_size = map_data.shape[0]
        
        for i in range(grid_size):
            for j in range(grid_size):
                country_id = map_data[i, j]
                if country_id not in country_positions:
                    country_positions[country_id] = []
                country_positions[country_id].append((j, i))
        
        for country_id, positions in country_positions.items():
            if country_id in country_names and len(positions) > 2:
                avg_x = sum(x for x, y in positions) / len(positions)
                avg_y = sum(y for x, y in positions) / len(positions)
                ax.text(avg_x, avg_y, country_names[country_id],
                       ha="center", va="center", fontsize=10, 
                       color="white", weight="bold",
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.5))
    
    return fig

# Streamlit UI
st.title("🗺️ Map Strategy Game")
st.markdown("Watch empires battle for territory in real-time!")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Game Settings")
    num_countries_random = st.slider("Countries for Random Map", 2, 30, 10)

    
    if st.button("🎲 New Game", type="primary"):
        map_data, countries, country_names, country_colors = initialize_predefined_map()
        st.session_state.map_data = map_data
        st.session_state.countries = countries
        st.session_state.country_names = country_names
        st.session_state.country_colors = country_colors
        st.session_state.turn_count = 0
        st.success("New game started!")
    
    if st.button("🌍 Generate Random Map"):
        map_data, country_names, country_colors = create_random_map(
        num_countries=num_countries_random,
        min_cells_per_country=10)
        st.session_state.map_data = map_data
        st.session_state.countries = {}
        # Build countries dictionary
        for country_id in np.unique(map_data):
            st.session_state.countries[country_id] = list(zip(*np.where(map_data == country_id)))

        st.session_state.country_names = country_names
        st.session_state.country_colors = country_colors
        st.session_state.turn_count = 0
        st.success("Random map generated!")

    st.divider()
    st.header("🎮 Game Controls")
    
    show_names = st.checkbox("Show Country Names", value=True)
    
    # Battle mode selection
    battle_mode = st.radio("Battle Mode", ["🎲 Random", "⚔️ Manual"])
    
    if battle_mode == "🎲 Random":
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Random Turn"):
                if st.session_state.map_data is not None:
                    success, attacker, defender = random_turn(
                        st.session_state.map_data, 
                        st.session_state.stable_countries, 
                        st.session_state.countries
                    )
                    if success:
                        st.session_state.turn_count += 1
                        attacker_name = st.session_state.country_names.get(attacker, f"Country {attacker}")
                        defender_name = st.session_state.country_names.get(defender, f"Country {defender}")
                        st.success(f"⚔️ {attacker_name} attacks {defender_name}!")
                        st.rerun()
                    else:
                        st.warning("No valid moves available!")
        
        with col2:
            num_turns = st.number_input("Turns to run", 1, 100, 10)
            if st.button("⏩ Run Multiple"):
                if st.session_state.map_data is not None:
                    battles = []
                    for _ in range(num_turns):
                        success, attacker, defender = random_turn(
                            st.session_state.map_data, 
                            st.session_state.stable_countries, 
                            st.session_state.countries
                        )
                        if not success:
                            break
                        st.session_state.turn_count += 1
                        if len(battles) < 5:
                            attacker_name = st.session_state.country_names.get(attacker, f"Country {attacker}")
                            defender_name = st.session_state.country_names.get(defender, f"Country {defender}")
                            battles.append(f"{attacker_name} vs {defender_name}")
                    
                    if battles:
                        st.success("Recent battles:\n" + "\n".join(f"⚔️ {b}" for b in battles))
                    st.rerun()
    
    else:  # Manual mode
        if st.session_state.map_data is not None:
            active_countries = []
            for c in st.session_state.countries.keys():
                if c not in st.session_state.stable_countries and np.any(st.session_state.map_data == c):
                    active_countries.append(c)
            
            if len(active_countries) >= 2:
                st.markdown("**Select Attacker:**")
                attacker_options = {f"{st.session_state.country_names[c]} (ID: {c})": c 
                                   for c in active_countries}
                attacker_name = st.selectbox("Attacker", list(attacker_options.keys()), key="attacker")
                attacker_id = attacker_options[attacker_name]
                
                st.markdown("**Select Defender:**")
                defender_candidates = [c for c in active_countries if c != attacker_id]
                defender_options = {f"{st.session_state.country_names[c]} (ID: {c})": c 
                                   for c in defender_candidates}
                defender_name = st.selectbox("Defender", list(defender_options.keys()), key="defender")
                defender_id = defender_options[defender_name]
                
                if st.button("⚔️ Attack!", type="primary"):
                    invade(st.session_state.map_data, attacker_id, defender_id)
                    st.session_state.turn_count += 1
                    st.success(f"⚔️ {st.session_state.country_names[attacker_id]} attacks {st.session_state.country_names[defender_id]}!")
                    st.rerun()
            else:
                st.warning("Not enough active countries for manual battle!")
        else:
            st.info("Start a new game to use manual mode!")
    
    st.divider()
    st.metric("Turn Count", st.session_state.turn_count)
    
    if st.session_state.map_data is not None:
        active_countries = []
        for c in st.session_state.countries.keys():
            if c not in st.session_state.stable_countries and np.any(st.session_state.map_data == c):
                active_countries.append(c)
        
        st.metric("Active Countries", len(active_countries))
        
        # Show country list
        if active_countries:
            st.subheader("🏴 Countries")
            for country_id in sorted(active_countries):
                territory_size = np.sum(st.session_state.map_data == country_id)
                country_name = st.session_state.country_names.get(country_id, f"Country {country_id}")
                color = st.session_state.country_colors.get(country_id, (0, 0, 0))
                color_hex = "#{:02x}{:02x}{:02x}".format(int(color[0]*255), int(color[1]*255), int(color[2]*255))
                st.markdown(f'<span style="color:{color_hex}">●</span> **{country_name}**: {territory_size} cells', 
                           unsafe_allow_html=True)

# Main display
if st.session_state.map_data is None:
    st.info("👈 Click 'New Game' in the sidebar to start!")
    st.markdown("### 🌍 Empires Ready for Battle:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- 🔵 **UU EMPIRE**")
        st.markdown("- 🟢 **YELIZ EMPIRE**")
        st.markdown("- 🔴 **STATE of SEDAT**")
        st.markdown("- 🟡 **UNITED KINGDOM**")
    with col2:
        st.markdown("- 🟣 **OTTOMANS**")
        st.markdown("- ⚫ **USA**")
        st.markdown("- 🌸 **GERMAN EMPIRE**")
        st.markdown("- 🟠 **USSR**")
else:
    fig = draw_map(st.session_state.map_data, st.session_state.country_colors, 
                   st.session_state.country_names, show_names)
    st.pyplot(fig)
    plt.close()