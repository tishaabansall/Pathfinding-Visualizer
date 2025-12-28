import numpy as np
import matplotlib.pyplot as plt
import heapq
from matplotlib.animation import FuncAnimation

# ================= CONFIG =================
GRID_SIZE = 20
anim = None

# Grid for pathfinding weights
weight_grid = np.ones((GRID_SIZE, GRID_SIZE))

# Grid for visualization
display_grid = np.ones((GRID_SIZE, GRID_SIZE))

start = None
end = None
steps = []
nodes_explored = 0

# ================= COLORS =================
START_END_COLOR = 30
VISITED_COLOR = 15
PATH_COLOR = 25
TRAFFIC_COLORS = {1:1, 5:5, 10:10}  # mapping for display

# ================= PLOT =================
fig, ax = plt.subplots()
im = ax.imshow(display_grid, cmap="YlOrRd", vmin=1, vmax=25)
info_text = ax.text(
    0.5, -0.08,
    "CLICK INSIDE GRID → Right click: Start/End | Press D (Dijkstra) or A (A*)",
    transform=ax.transAxes,
    ha="center",
    fontsize=10,
    color="black"
)

# ================= HELPERS =================
def get_neighbors(node):
    r, c = node
    neighbors = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            neighbors.append((nr, nc))
    return neighbors

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ================= DIJKSTRA =================
def dijkstra_steps(start_node, end_node):
    global nodes_explored
    nodes_explored = 0
    dist = {start_node: 0}
    prev = {}
    pq = [(0, start_node)]
    visited = set()
    local_steps = []

    while pq:
        cost, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        nodes_explored += 1
        local_steps.append(("visit", node))

        if node == end_node:
            break

        for nbr in get_neighbors(node):
            new_cost = cost + weight_grid[nbr]
            if new_cost < dist.get(nbr, float("inf")):
                dist[nbr] = new_cost
                prev[nbr] = node
                heapq.heappush(pq, (new_cost, nbr))

    # Reconstruct path
    node = end_node
    path = []
    while node in prev:
        path.append(node)
        node = prev[node]
    path.append(start_node)
    path.reverse()
    for p in path:
        local_steps.append(("path", p))

    info_text.set_text(f"Dijkstra | Nodes explored: {nodes_explored}")
    print(f"Dijkstra → Nodes explored: {nodes_explored}")
    return local_steps

# ================= A* =================
def astar_steps(start_node, end_node):
    global nodes_explored
    nodes_explored = 0
    g = {start_node: 0}
    prev = {}
    pq = [(heuristic(start_node, end_node), start_node)]
    visited = set()
    local_steps = []

    while pq:
        _, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        nodes_explored += 1
        local_steps.append(("visit", node))

        if node == end_node:
            break

        for nbr in get_neighbors(node):
            tentative = g[node] + weight_grid[nbr]
            if tentative < g.get(nbr, float("inf")):
                g[nbr] = tentative
                prev[nbr] = node
                f = tentative + heuristic(nbr, end_node)
                heapq.heappush(pq, (f, nbr))

    # Reconstruct path
    node = end_node
    path = []
    while node in prev:
        path.append(node)
        node = prev[node]
    path.append(start_node)
    path.reverse()
    for p in path:
        local_steps.append(("path", p))

    info_text.set_text(f"A* | Nodes explored: {nodes_explored}")
    print(f"A* → Nodes explored: {nodes_explored}")
    return local_steps

# ================= ANIMATION =================
def animate(i):
    if i >= len(steps):
        return
    action, cell = steps[i]
    r, c = cell

    if action == "visit" and cell != start and cell != end:
        display_grid[r, c] = VISITED_COLOR
    elif action == "path" and cell != start and cell != end:
        display_grid[r, c] = PATH_COLOR

    # Highlight start/end with same color
    if start:
        display_grid[start] = START_END_COLOR
    if end:
        display_grid[end] = START_END_COLOR

    im.set_data(display_grid)

# ================= INTERACTION =================
def onclick(event):
    global start, end, weight_grid, display_grid
    if event.inaxes != ax:
        return
    r = int(np.clip(event.ydata + 0.5, 0, GRID_SIZE-1))
    c = int(np.clip(event.xdata + 0.5, 0, GRID_SIZE-1))

    if event.button == 1:  # toggle traffic
        if (r,c) != start and (r,c) != end:
            weight_grid[r, c] = {1:5, 5:10, 10:1}[weight_grid[r, c]]
            display_grid[r, c] = TRAFFIC_COLORS[weight_grid[r, c]]
    elif event.button == 3:  # set start/end
        if start is None:
            start = (r,c)
            display_grid[start] = START_END_COLOR
            print("Start:", start)
        elif end is None:
            end = (r,c)
            display_grid[end] = START_END_COLOR
            print("End:", end)
    im.set_data(display_grid)
    plt.draw()

def onkey(event):
    global steps, display_grid, start, end, anim
    if event.key.lower() == "d" and start and end:
        display_grid[:] = weight_grid
        steps = dijkstra_steps(start, end)
        anim = FuncAnimation(fig, animate, frames=len(steps), interval=40, repeat=False)
    elif event.key.lower() == "a" and start and end:
        display_grid[:] = weight_grid
        steps = astar_steps(start, end)
        anim = FuncAnimation(fig, animate, frames=len(steps), interval=40, repeat=False)
    elif event.key.lower() == "r":
        weight_grid[:] = 1
        display_grid[:] = 1
        start = None
        end = None
        steps.clear()
        anim = None
        info_text.set_text(
            "CLICK INSIDE GRID → Right click: Start/End | Press D (Dijkstra) or A (A*)"
        )
        im.set_data(display_grid)
        plt.draw()

# ================= BIND =================
fig.canvas.mpl_connect("button_press_event", onclick)
fig.canvas.mpl_connect("key_press_event", onkey)
plt.title(
    "Left click: Traffic | Right click: Start/End | D: Dijkstra | A: A* | R: Reset"
)
plt.show()
