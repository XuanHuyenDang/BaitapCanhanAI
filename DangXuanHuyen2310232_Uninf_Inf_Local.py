import pygame
from collections import deque
import heapq
import time
import random
import math

# ======= Pygame Configuration =======
WIDTH, HEIGHT = 1280, 720  # Adjusted for ~14-inch display
TILE_SIZE = 80  # Scaled up for larger window
# Modern color palette
BACKGROUND = (245, 245, 250)  # Soft off-white
BLACK = (0, 0, 0)
PRIMARY = (100, 181, 246)  # Soft sky blue for buttons
ACCENT = (255, 128, 171)  # Coral for highlights
SUCCESS = (129, 199, 132)  # Light green for valid tiles
ERROR = (239, 83, 80)  # Soft red for blank tiles
HIGHLIGHT = (255, 245, 157)  # Light yellow for selected tiles
HOVER = (144, 202, 249)  # Lighter blue for button hover
BORDER = (66, 66, 66)  # Dark gray for borders
GRAY = (128, 128, 128)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("8 Puzzle Solver")
clock = pygame.time.Clock()

# ======= Fonts =======
font = pygame.font.SysFont("Segoe UI", 32)  # Larger font for larger window
small_font = pygame.font.SysFont("Segoe UI", 20)

# ======= Global Variables =======
initial_state_input = [""] * 9
goal_state_input = [""] * 9
INITIAL_STATE = tuple()
GOAL_STATE = tuple()
steps_display = []
scroll_offset = 0
max_steps_visible = 6  # Adjusted for larger window
selected_tile = None  # Tracks tile being edited (index, grid: 'initial' or 'goal')
states_confirmed = False
input_message = ""

# ======= Helper Functions =======
def get_blank_index(state):
    try:
        return state.index("")
    except ValueError:
        raise ValueError("State must contain one blank tile!")
        
def get_neighbors(index):
    moves = {
        0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
        3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
        6: [3, 7], 7: [4, 6, 8], 8: [5, 7]
    }
    return moves[index]

def swap_positions(state, blank_index, move):
    state = list(state)
    state[blank_index], state[move] = state[move], state[blank_index]
    return tuple(state)

# ======= Manhattan Distance Heuristic =======
def manhattan_distance(state):
    distance = 0
    for i, value in enumerate(state):
        if value == "":
            continue
        target_index = GOAL_STATE.index(value)
        x1, y1 = i % 3, i // 3
        x2, y2 = target_index % 3, target_index // 3
        distance += abs(x1 - x2) + abs(y1 - y2)
    return distance

# ======= Belief State Heuristic =======
def heuristic_belief(belief_state):
    if not belief_state:
        return float('inf')
    return min(manhattan_distance(state) for state in belief_state)

# ======= Greedy Search Algorithm =======
def greedy_search_solve(initial_state):
    start_time = time.time()
    queue = [(manhattan_distance(initial_state), initial_state, [])]
    visited = set([initial_state])
    while queue:
        _, current_state, path = heapq.heappop(queue)
        if current_state == GOAL_STATE:
            return path, time.time() - start_time
        blank_index = get_blank_index(current_state)
        for move in get_neighbors(blank_index):
            new_state = swap_positions(current_state, blank_index, move)
            if new_state not in visited:
                visited.add(new_state)
                heapq.heappush(queue, (manhattan_distance(new_state), new_state, path + [new_state]))
    return None, time.time() - start_time

# ======= BFS Algorithm =======
def bfs_solve(initial_state):
    start_time = time.time()
    queue = deque([(initial_state, [])])
    visited = set([initial_state])
    while queue:
        current_state, path = queue.popleft()
        if current_state == GOAL_STATE:
            return path, time.time() - start_time
        blank_index = get_blank_index(current_state)
        for move in get_neighbors(blank_index):
            new_state = swap_positions(current_state, blank_index, move)
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [new_state]))
    return None, time.time() - start_time

# ======= DFS Algorithm =======
def dfs_solve(initial_state):
    start_time = time.time()
    stack = [(initial_state, [], 0)]
    visited = set([initial_state])
    while stack:
        current_state, path, depth = stack.pop()
        if current_state == GOAL_STATE:
            return path, time.time() - start_time
        if depth >= 50:
            continue
        blank_index = get_blank_index(current_state)
        for move in reversed(get_neighbors(blank_index)):
            new_state = swap_positions(current_state, blank_index, move)
            if new_state not in visited:
                visited.add(new_state)
                stack.append((new_state, path + [new_state], depth + 1))
    return None, time.time() - start_time

# ======= IDS Algorithm =======
def ids_solve(initial_state):
    start_time = time.time()
    def dfs_limited(state, path, depth, limit):
        if state == GOAL_STATE:
            return path
        if depth == limit:
            return None
        blank_index = get_blank_index(state)
        for move in get_neighbors(blank_index):
            new_state = swap_positions(state, blank_index, move)
            if new_state not in path:
                result = dfs_limited(new_state, path + [new_state], depth + 1, limit)
                if result:
                    return result
        return None
    limit = 0
    while True:
        result = dfs_limited(initial_state, [], 0, limit)
        if result:
            return result, time.time() - start_time
        limit += 1

# ======= UCS Algorithm =======
def ucs_solve(initial_state):
    start_time = time.time()
    queue = [(0, initial_state, [])]
    visited = set([initial_state])
    while queue:
        cost, current_state, path = heapq.heappop(queue)
        if current_state == GOAL_STATE:
            return path, time.time() - start_time
        blank_index = get_blank_index(current_state)
        for move in get_neighbors(blank_index):
            new_state = swap_positions(current_state, blank_index, move)
            if new_state not in visited:
                visited.add(new_state)
                heapq.heappush(queue, (cost + 1, new_state, path + [new_state]))
    return None, time.time() - start_time

# ======= A* Algorithm =======
def a_star_solve(initial_state):
    start_time = time.time()
    queue = [(manhattan_distance(initial_state), 0, initial_state, [])]
    visited = set([initial_state])
    while queue:
        f_score, g_score, current_state, path = heapq.heappop(queue)
        if current_state == GOAL_STATE:
            return path, time.time() - start_time
        blank_index = get_blank_index(current_state)
        for move in get_neighbors(blank_index):
            new_state = swap_positions(current_state, blank_index, move)
            if new_state not in visited:
                visited.add(new_state)
                new_g_score = g_score + 1
                new_h_score = manhattan_distance(new_state)
                new_f_score = new_g_score + new_h_score
                heapq.heappush(queue, (new_f_score, new_g_score, new_state, path + [new_state]))
    return None, time.time() - start_time

# ======= IDA* Algorithm =======
def ida_star_solve(initial_state):
    start_time = time.time()
    def search(state, g_score, bound, path, visited):
        h_score = manhattan_distance(state)
        f_score = g_score + h_score
        if f_score > bound:
            return None, f_score
        if state == GOAL_STATE:
            return path, f_score
        min_f = float('inf')
        blank_index = get_blank_index(state)
        for move in get_neighbors(blank_index):
            new_state = swap_positions(state, blank_index, move)
            if new_state not in visited:
                visited.add(new_state)
                result, next_f = search(new_state, g_score + 1, bound, path + [new_state], visited)
                visited.remove(new_state)
                if result is not None:
                    return result, f_score
                min_f = min(min_f, next_f)
        return None, min_f
    bound = manhattan_distance(initial_state)
    visited = {initial_state}
    while True:
        result, t = search(initial_state, 0, bound, [initial_state], visited)
        if result is not None:
            return result[1:], time.time() - start_time
        if t == float('inf'):
            return None, time.time() - start_time
        bound = t

# ======= Steepest Hill Climbing Algorithm =======
def steepest_hill_climbing_solve(initial_state):
    start_time = time.time()
    current_state = initial_state
    path = [current_state]
    visited = set([current_state])
    while current_state != GOAL_STATE:
        blank_index = get_blank_index(current_state)
        neighbors = get_neighbors(blank_index)
        best_state = None
        best_heuristic = float('inf')
        for move in neighbors:
            new_state = swap_positions(current_state, blank_index, move)
            if new_state not in visited:
                h = manhattan_distance(new_state)
                if h < best_heuristic:
                    best_heuristic = h
                    best_state = new_state
        if best_state is None or best_heuristic >= manhattan_distance(current_state):
            return None, time.time() - start_time
        current_state = best_state
        visited.add(current_state)
        path.append(current_state)
    return path, time.time() - start_time

# ======= Stochastic Hill Climbing Algorithm =======
def stochastic_hill_climbing_solve(initial_state):
    start_time = time.time()
    current_state = initial_state
    path = [current_state]
    visited = set([current_state])
    while current_state != GOAL_STATE:
        blank_index = get_blank_index(current_state)
        neighbors = get_neighbors(blank_index)
        current_heuristic = manhattan_distance(current_state)
        better_neighbors = []
        for move in neighbors:
            new_state = swap_positions(current_state, blank_index, move)
            if new_state not in visited:
                h = manhattan_distance(new_state)
                if h < current_heuristic:
                    better_neighbors.append(new_state)
        if not better_neighbors:
            return None, time.time() - start_time
        current_state = random.choice(better_neighbors)
        visited.add(current_state)
        path.append(current_state)
    return path, time.time() - start_time

# ======= Simple Hill Climbing Algorithm =======
def simple_hill_climbing_solve(initial_state):
    start_time = time.time()
    current_state = initial_state
    path = [current_state]
    visited = set([current_state])
    while current_state != GOAL_STATE:
        blank_index = get_blank_index(current_state)
        neighbors = get_neighbors(blank_index)
        current_heuristic = manhattan_distance(current_state)
        for move in neighbors:
            new_state = swap_positions(current_state, blank_index, move)
            if new_state not in visited:
                h = manhattan_distance(new_state)
                if h < current_heuristic:
                    current_state = new_state
                    visited.add(current_state)
                    path.append(current_state)
                    break
        else:
            return None, time.time() - start_time
    return path, time.time() - start_time

# ======= Simulated Annealing Algorithm =======
def simulated_annealing_solve(initial_state):
    start_time = time.time()
    current_state = initial_state
    path = [current_state]
    temperature = 1000.0
    cooling_rate = 0.995
    min_temperature = 0.01
    while current_state != GOAL_STATE and temperature > min_temperature:
        blank_index = get_blank_index(current_state)
        neighbors = get_neighbors(blank_index)
        current_cost = manhattan_distance(current_state)
        next_move = random.choice(neighbors)
        next_state = swap_positions(current_state, blank_index, next_move)
        next_cost = manhattan_distance(next_state)
        cost_diff = next_cost - current_cost
        if cost_diff < 0 or random.random() < math.exp(-cost_diff / temperature):
            current_state = next_state
            path.append(current_state)
        temperature *= cooling_rate
    if current_state == GOAL_STATE:
        return path, time.time() - start_time
    return None, time.time() - start_time

# ======= Beam Search Algorithm =======
def beam_search_solve(initial_state, beam_width=3):
    start_time = time.time()
    queue = [(manhattan_distance(initial_state), initial_state, [])]
    visited = set([initial_state])
    while queue:
        queue = heapq.nsmallest(beam_width, queue)
        next_queue = []
        for h, current_state, path in queue:
            if current_state == GOAL_STATE:
                return path, time.time() - start_time
            blank_index = get_blank_index(current_state)
            for move in get_neighbors(blank_index):
                new_state = swap_positions(current_state, blank_index, move)
                if new_state not in visited:
                    visited.add(new_state)
                    new_h = manhattan_distance(new_state)
                    next_queue.append((new_h, new_state, path + [new_state]))
        queue = heapq.nsmallest(beam_width, next_queue)
    return None, time.time() - start_time

# ======= Genetic Algorithm =======
def genetic_algorithm_solve(initial_state, population_size=100, generations=500, mutation_rate=0.1):
    start_time = time.time()
    def generate_individual():
        state = list(initial_state)
        moves = []
        for _ in range(random.randint(5, 20)):
            blank_idx = state.index("")
            possible_moves = get_neighbors(blank_idx)
            move = random.choice(possible_moves)
            state[blank_idx], state[move] = state[move], state[blank_idx]
            moves.append(tuple(state))
        return moves
    def fitness(individual):
        if not individual:
            return float('inf')
        final_state = individual[-1]
        return manhattan_distance(final_state)
    def crossover(parent1, parent2):
        if not parent1 or not parent2:
            return parent1 if parent1 else parent2
        split = random.randint(0, min(len(parent1), len(parent2)) - 1)
        child = parent1[:split] + parent2[split:]
        return child
    def mutate(individual):
        if random.random() < mutation_rate and individual:
            idx = random.randint(0, len(individual) - 1)
            state = list(individual[idx])
            blank_idx = state.index("")
            possible_moves = get_neighbors(blank_idx)
            move = random.choice(possible_moves)
            state[blank_idx], state[move] = state[move], state[blank_idx]
            individual[idx:] = [tuple(state)]
        return individual
    population = [generate_individual() for _ in range(population_size)]
    for _ in range(generations):
        population = sorted(population, key=fitness)
        if fitness(population[0]) == 0:
            return population[0], time.time() - start_time
        elite_size = population_size // 10
        new_population = population[:elite_size]
        while len(new_population) < population_size:
            parent1 = random.choice(population[:population_size // 2])
            parent2 = random.choice(population[:population_size // 2])
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
        population = new_population[:population_size]
    best_individual = min(population, key=fitness)
    if fitness(best_individual) == 0:
        return best_individual, time.time() - start_time
    return None, time.time() - start_time

# # ======= AND-OR Graph Search Algorithm =======
# def and_or_search_solve(initial_state):
#     start_time = time.time()
#     visited = set()
#     def or_search(state, path, depth):
#         if state == GOAL_STATE:
#             return []
#         if state in visited or depth > 50:
#             return None
#         visited.add(state)
#         blank_index = get_blank_index(state)
#         for move in get_neighbors(blank_index):
#             new_state = swap_positions(state, blank_index, move)
#             plan = and_search([new_state], path + [state], depth + 1)
#             if plan is not None:
#                 return [new_state] + plan
#         return None
#     def and_search(states, path, depth):
#         for state in states:
#             plan = or_search(state, path, depth)
#             if plan is None:
#                 return None
#             return plan
#         return []
#     result = or_search(initial_state, [], 0)
#     return result, time.time() - start_time

# ======= Draw Button =======
def draw_button(x, y, width, height, text, color, enabled=True):
    """Draw a button with hover effect."""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    is_hover = x <= mouse_x <= x + width and y <= mouse_y <= y + height and enabled
    button_color = HOVER if is_hover else color
    if not enabled:
        button_color = GRAY
    pygame.draw.rect(screen, button_color, (x, y, width, height), border_radius=12)
    pygame.draw.rect(screen, BORDER, (x, y, width, height), 2, border_radius=12)
    button_font = pygame.font.SysFont("Segoe UI", 24)
    text_render = button_font.render(text, True, BLACK)
    text_rect = text_render.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_render, text_rect)

# ======= Draw Main Interface =======
def draw_board(initial_state, goal_state, current_state=None, message="", execution_time=None):
    """Draw the state boards, algorithm buttons, and result area."""
    global scroll_offset, selected_tile, input_message
    screen.fill(BACKGROUND)

    # Draw "Initial State" label and grid
    initial_label = small_font.render("Initial State", True, BLACK)
    screen.blit(initial_label, (30, 20))
    for i in range(3):
        for j in range(3):
            value = initial_state[i * 3 + j]
            x, y = 30 + j * TILE_SIZE, 60 + i * TILE_SIZE
            color = SUCCESS if value != "" else ERROR
            if selected_tile and selected_tile[0] == i * 3 + j and selected_tile[1] == 'initial':
                color = HIGHLIGHT
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE), border_radius=8)
            pygame.draw.rect(screen, BORDER, (x, y, TILE_SIZE, TILE_SIZE), 2, border_radius=8)
            if value != "":
                text = font.render(value, True, BLACK)
                text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                screen.blit(text, text_rect)

    # Draw "Goal State" label and grid
    goal_label = small_font.render("Goal State", True, BLACK)
    screen.blit(goal_label, (300, 20))
    for i in range(3):
        for j in range(3):
            value = goal_state[i * 3 + j]
            x, y = 300 + j * TILE_SIZE, 60 + i * TILE_SIZE
            color = SUCCESS if value != "" else ERROR
            if selected_tile and selected_tile[0] == i * 3 + j and selected_tile[1] == 'goal':
                color = HIGHLIGHT
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE), border_radius=8)
            pygame.draw.rect(screen, BORDER, (x, y, TILE_SIZE, TILE_SIZE), 2, border_radius=8)
            if value != "":
                text = font.render(value, True, BLACK)
                text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                screen.blit(text, text_rect)

    # Draw "Solving State" label and grid
    solving_label = small_font.render("Solving State", True, BLACK)
    screen.blit(solving_label, (30, 320))
    display_state = current_state if current_state else initial_state
    for i in range(3):
        for j in range(3):
            value = display_state[i * 3 + j]
            x, y = 30 + j * TILE_SIZE, 360 + i * TILE_SIZE
            color = SUCCESS if value != "" else ERROR
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE), border_radius=8)
            pygame.draw.rect(screen, BORDER, (x, y, TILE_SIZE, TILE_SIZE), 2, border_radius=8)
            if value != "":
                text = font.render(value, True, BLACK)
                text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                screen.blit(text, text_rect)

    # Draw algorithm buttons in two columns
    button_y_start = 60
    button_spacing = 50
    button_width = 140
    button_height = 40
    left_column_x = 650
    right_column_x = 820

    # Left column
    draw_button(left_column_x, button_y_start, button_width, button_height, "DFS", PRIMARY, states_confirmed)
    draw_button(left_column_x, button_y_start + button_spacing, button_width, button_height, "IDS", PRIMARY, states_confirmed)
    draw_button(left_column_x, button_y_start + 2 * button_spacing, button_width, button_height, "A*", PRIMARY, states_confirmed)
    draw_button(left_column_x, button_y_start + 3 * button_spacing, button_width, button_height, "BFS", PRIMARY, states_confirmed)
    draw_button(left_column_x, button_y_start + 4 * button_spacing, button_width, button_height, "UCS", PRIMARY, states_confirmed)
    draw_button(left_column_x, button_y_start + 5 * button_spacing, button_width, button_height, "GREEDY", PRIMARY, states_confirmed)
    draw_button(left_column_x, button_y_start + 6 * button_spacing, button_width, button_height, "IDA*", PRIMARY, states_confirmed)

    # Right column
    draw_button(right_column_x, button_y_start, button_width, button_height, "STEEPEST", PRIMARY, states_confirmed)
    draw_button(right_column_x, button_y_start + button_spacing, button_width, button_height, "STOCHASTIC", PRIMARY, states_confirmed)
    draw_button(right_column_x, button_y_start + 2 * button_spacing, button_width, button_height, "SIMPLE", PRIMARY, states_confirmed)
    draw_button(right_column_x, button_y_start + 3 * button_spacing, button_width, button_height, "SIMULATED", PRIMARY, states_confirmed)
    draw_button(right_column_x, button_y_start + 4 * button_spacing, button_width, button_height, "BEAM", PRIMARY, states_confirmed)
    draw_button(right_column_x, button_y_start + 5 * button_spacing, button_width, button_height, "GENETIC", PRIMARY, states_confirmed)
    # draw_button(right_column_x, button_y_start + 6 * button_spacing, button_width, button_height, "AND-OR", PRIMARY, states_confirmed)

    # Draw "Program Output" area
    running_label = small_font.render("Program Output", True, BLACK)
    screen.blit(running_label, (650, 450))
    pygame.draw.rect(screen, BORDER, (650, 480, 600, 220), 2, border_radius=8)

    # Display running algorithm and execution time
    algo_label = small_font.render("Running Algorithm:", True, BLACK)
    screen.blit(algo_label, (670, 490))
    if message:
        algo_text = small_font.render(message, True, BLACK)
        screen.blit(algo_text, (670, 520))
    if execution_time is not None:
        time_text = small_font.render(f"Execution Time: {execution_time:.4f}s", True, BLACK)
        screen.blit(time_text, (670, 550))

    # Display solution steps
    steps_label = small_font.render("Solution Steps:", True, BLACK)
    screen.blit(steps_label, (670, 580))
    step_y_start = 610
    step_spacing = 25
    for i, step in enumerate(steps_display):
        if i < scroll_offset:
            continue
        if i >= scroll_offset + max_steps_visible:
            break
        step_text = small_font.render(f"Step {i + 1}: {step}", True, BLACK)
        screen.blit(step_text, (670, step_y_start + (i - scroll_offset) * step_spacing))

    # Draw "Confirm" button (only shown before states are confirmed)
    if not states_confirmed:
        draw_button(300, 320, 120, 40, "Confirm", ACCENT)

    # Draw input message
    if input_message:
        message_text = small_font.render(input_message, True, BLACK)
        screen.blit(message_text, (300, 280))

    # Draw "Exit" button
    draw_button(WIDTH - 100, 20, 80, 40, "Exit", PRIMARY)
    pygame.display.flip()

# ======= Run Program =======
def main():
    """Main function to control the program."""
    global INITIAL_STATE, GOAL_STATE, steps_display, scroll_offset, selected_tile, states_confirmed, input_message
    selected_algorithm = None
    execution_time = None

    # State input phase
    while not states_confirmed:
        draw_board(initial_state_input, goal_state_input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Check click on "Initial State" grid
                if 30 <= x < 30 + TILE_SIZE * 3 and 60 <= y < 60 + TILE_SIZE * 3:
                    tile_x, tile_y = (x - 30) // TILE_SIZE, (y - 60) // TILE_SIZE
                    selected_index = tile_y * 3 + tile_x
                    selected_tile = (selected_index, 'initial')
                    input_message = ""
                # Check click on "Goal State" grid
                elif 300 <= x < 300 + TILE_SIZE * 3 and 60 <= y < 60 + TILE_SIZE * 3:
                    tile_x, tile_y = (x - 300) // TILE_SIZE, (y - 60) // TILE_SIZE
                    selected_index = tile_y * 3 + tile_x
                    selected_tile = (selected_index, 'goal')
                    input_message = ""
                # Check click on "Confirm" button
                elif 300 <= x <= 420 and 320 <= y <= 360:
                    # Validate states
                    for state, state_name in [(initial_state_input, "initial"), (goal_state_input, "goal")]:
                        blank_count = state.count("")
                        if blank_count != 1:
                            input_message = f"{state_name.capitalize()} state must have 1 blank tile!"
                            break
                        numbers = [x for x in state if x != ""]
                        if len(numbers) != 8 or set(numbers) != set(["1", "2", "3", "4", "5", "6", "7", "8"]):
                            input_message = f"{state_name.capitalize()} state must contain numbers 1-8!"
                            break
                    else:
                        states_confirmed = True
                        INITIAL_STATE = tuple(initial_state_input)
                        GOAL_STATE = tuple(goal_state_input)
                        input_message = "States confirmed! Select an algorithm."
                        print(f"Initial State: {INITIAL_STATE}")
                        print(f"Goal State: {GOAL_STATE}")
                # Check click on "Exit" button
                elif WIDTH - 100 <= x <= WIDTH - 20 and 20 <= y <= 60:
                    pygame.quit()
                    return
            elif event.type == pygame.KEYDOWN and selected_tile:
                index, grid = selected_tile
                key = event.unicode
                if key in "12345678":
                    if grid == 'initial':
                        initial_state_input[index] = key
                    else:
                        goal_state_input[index] = key
                    selected_tile = None
                    input_message = ""
                elif event.key == pygame.K_SPACE:
                    if grid == 'initial':
                        initial_state_input[index] = ""
                    else:
                        goal_state_input[index] = ""
                    selected_tile = None
                    input_message = ""
        clock.tick(30)

    # Algorithm selection and solving phase
    while True:
        selected_algorithm = None
        execution_time = None
        steps_display = []
        scroll_offset = 0
        running = True

        while running:
            draw_board(INITIAL_STATE, GOAL_STATE, message="Select an algorithm:")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    button_y_start = 60
                    button_spacing = 50
                    button_width = 140
                    button_height = 40
                    left_column_x = 650
                    right_column_x = 820
                    if left_column_x <= x <= left_column_x + button_width:
                        if button_y_start <= y <= button_y_start + button_height:
                            selected_algorithm = "dfs"
                            running = False
                        elif button_y_start + button_spacing <= y <= button_y_start + button_spacing + button_height:
                            selected_algorithm = "ids"
                            running = False
                        elif button_y_start + 2 * button_spacing <= y <= button_y_start + 2 * button_spacing + button_height:
                            selected_algorithm = "a_star"
                            running = False
                        elif button_y_start + 3 * button_spacing <= y <= button_y_start + 3 * button_spacing + button_height:
                            selected_algorithm = "bfs"
                            running = False
                        elif button_y_start + 4 * button_spacing <= y <= button_y_start + 4 * button_spacing + button_height:
                            selected_algorithm = "ucs"
                            running = False
                        elif button_y_start + 5 * button_spacing <= y <= button_y_start + 5 * button_spacing + button_height:
                            selected_algorithm = "greedy"
                            running = False
                        elif button_y_start + 6 * button_spacing <= y <= button_y_start + 6 * button_spacing + button_height:
                            selected_algorithm = "ida_star"
                            running = False
                    elif right_column_x <= x <= right_column_x + button_width:
                        if button_y_start <= y <= button_y_start + button_height:
                            selected_algorithm = "steepest"
                            running = False
                        elif button_y_start + button_spacing <= y <= button_y_start + button_spacing + button_height:
                            selected_algorithm = "stochastic"
                            running = False
                        elif button_y_start + 2 * button_spacing <= y <= button_y_start + 2 * button_spacing + button_height:
                            selected_algorithm = "simple"
                            running = False
                        elif button_y_start + 3 * button_spacing <= y <= button_y_start + 3 * button_spacing + button_height:
                            selected_algorithm = "simulated"
                            running = False
                        elif button_y_start + 4 * button_spacing <= y <= button_y_start + 4 * button_spacing + button_height:
                            selected_algorithm = "beam"
                            running = False
                        elif button_y_start + 5 * button_spacing <= y <= button_y_start + 5 * button_spacing + button_height:
                            selected_algorithm = "genetic"
                            running = False
                        # elif button_y_start + 6 * button_spacing <= y <= button_y_start + 6 * button_spacing + button_height:
                        #     selected_algorithm = "and_or"
                        #     running = False
                    elif WIDTH - 100 <= x <= WIDTH - 20 and 20 <= y <= 60:
                        pygame.quit()
                        return
            clock.tick(30)

        print(f"Running algorithm: {selected_algorithm.upper()}")
        try:
            if selected_algorithm == "bfs":
                solution_path, execution_time = bfs_solve(INITIAL_STATE)
            elif selected_algorithm == "dfs":
                solution_path, execution_time = dfs_solve(INITIAL_STATE)
            elif selected_algorithm == "ids":
                solution_path, execution_time = ids_solve(INITIAL_STATE)
            elif selected_algorithm == "ucs":
                solution_path, execution_time = ucs_solve(INITIAL_STATE)
            elif selected_algorithm == "greedy":
                solution_path, execution_time = greedy_search_solve(INITIAL_STATE)
            elif selected_algorithm == "a_star":
                solution_path, execution_time = a_star_solve(INITIAL_STATE)
            elif selected_algorithm == "ida_star":
                solution_path, execution_time = ida_star_solve(INITIAL_STATE)
            elif selected_algorithm == "steepest":
                solution_path, execution_time = steepest_hill_climbing_solve(INITIAL_STATE)
            elif selected_algorithm == "stochastic":
                solution_path, execution_time = stochastic_hill_climbing_solve(INITIAL_STATE)
            elif selected_algorithm == "simple":
                solution_path, execution_time = simple_hill_climbing_solve(INITIAL_STATE)
            elif selected_algorithm == "simulated":
                solution_path, execution_time = simulated_annealing_solve(INITIAL_STATE)
            elif selected_algorithm == "beam":
                solution_path, execution_time = beam_search_solve(INITIAL_STATE)
            elif selected_algorithm == "genetic":
                solution_path, execution_time = genetic_algorithm_solve(INITIAL_STATE)
            # elif selected_algorithm == "and_or":
            #     solution_path, execution_time = and_or_search_solve(INITIAL_STATE)

            if solution_path:
                print(f"Solution found with {len(solution_path)} steps:")
                steps_display = []
                print(f"Step 0: {INITIAL_STATE}")
                steps_display = [str(INITIAL_STATE)]
                for i, state in enumerate(solution_path, 1):
                    print(f"Step {i}: {state}")
                    steps_display.append(str(state))
                    draw_board(INITIAL_STATE, GOAL_STATE, state, selected_algorithm.upper(), execution_time)
                    pygame.time.delay(500)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            x, y = event.pos
                            if WIDTH - 100 <= x <= WIDTH - 20 and 20 <= y <= 60:
                                pygame.quit()
                                return
                draw_board(INITIAL_STATE, GOAL_STATE, GOAL_STATE, "Completed!", execution_time)
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            x, y = event.pos
                            if WIDTH - 100 <= x <= WIDTH - 20 and 20 <= y <= 60:
                                pygame.quit()
                                return
                        elif event.type == pygame.MOUSEWHEEL:
                            if len(steps_display) > max_steps_visible:
                                scroll_offset = max(0, min(scroll_offset - event.y, len(steps_display) - max_steps_visible))
                    draw_board(INITIAL_STATE, GOAL_STATE, GOAL_STATE, "Completed!", execution_time)
                    clock.tick(30)
            else:
                print("No solution found")
                draw_board(INITIAL_STATE, GOAL_STATE, message="No solution found! Select another algorithm", execution_time=execution_time)
                pygame.time.delay(2000)
        except ValueError as e:
            print(f"Error: {e}")
            draw_board(INITIAL_STATE, GOAL_STATE, message=f"Error: {str(e)}! Select another algorithm", execution_time=execution_time)
            pygame.time.delay(2000)

if __name__ == "__main__":
    main()