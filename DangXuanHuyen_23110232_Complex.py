import pygame
import heapq
import time
import platform
import asyncio
import random
from collections import deque
import multiprocessing
import sys

class EightPuzzle:
    def __init__(self, initial, goals):
        self.initial = tuple(map(tuple, initial))
        self.goals = [tuple(map(tuple, goal)) for goal in goals]
        self.goal_state_indices = []
        for goal in self.goals:
            self.goal_state_indices.append({goal[i][j]: (i, j) for i in range(3) for j in range(3)})

    def find_blank(self, state):
        for i, row in enumerate(state):
            if 0 in row:
                return i, row.index(0)

    def get_neighbors(self, state):
        row, col = self.find_blank(state)
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        state_list = [list(row) for row in state]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_state = [row[:] for row in state_list]
                new_state[row][col], new_state[new_row][new_col] = new_state[new_row][new_col], new_state[row][col]
                moves.append(tuple(map(tuple, new_state)))
        return moves

    def manhattan_distance(self, state, goal_idx):
        distance = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != 0:
                    goal_x, goal_y = self.goal_state_indices[goal_idx][state[i][j]]
                    distance += abs(i - goal_x) + abs(j - goal_y)
        return distance

    def get_observation(self, state):
        for i in range(3):
            for j in range(3):
                if state[i][j] == 1:
                    return (i, j)
        return None

    def generate_fixed_belief_states(self):
        return [
            tuple(map(tuple, [[1, 2, 3], [4, 5, 6], [7, 0, 8]])),
            tuple(map(tuple, [[1, 2, 3], [4, 0, 6], [7, 5, 8]])),
            tuple(map(tuple, [[1, 2, 3], [0, 5, 6], [4, 7, 8]])),
            tuple(map(tuple, [[1, 2, 0], [4, 5, 3], [7, 8, 6]])),
        ]

    def and_or_search_single(self, target_goal, max_steps=1000):
        queue = deque([(self.initial, [self.initial])])
        visited = set([self.initial])
        steps = 0

        while queue and steps < max_steps:
            state, path = queue.popleft()
            steps += 1

            if state == target_goal:
                print("Đã tìm thấy đường đi:", path)  # Debug: In đường đi
                return path

            neighbors = self.get_neighbors(state)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        print("Không tìm thấy đường đi trong", max_steps, "bước")  # Debug
        return None

    def belief_state_search(self, max_states=4):
        initial_belief = set(self.generate_fixed_belief_states())
        pq = []
        heapq.heappush(pq, (0, 0, initial_belief, [list(initial_belief)[0]], [initial_belief.copy()]))
        visited = {}
        while pq:
            time.sleep(0.1)
            f, g, belief, path, belief_history = heapq.heappop(pq)
            belief_key = frozenset(belief)
            if belief_key in visited and visited[belief_key] <= f:
                continue
            visited[belief_key] = f
            for state in belief:
                for goal in self.goals:
                    if state == goal:
                        return path, list(belief), belief_history
            new_belief = set()
            for state in belief:
                new_belief.update(self.get_neighbors(state))
            if len(new_belief) > max_states:
                new_belief = set(sorted(new_belief, key=lambda s: min(self.manhattan_distance(s, i) for i in range(len(self.goals))) + g)[:max_states])
            if not new_belief:
                continue
            new_g = g + 1
            min_h = min(min(self.manhattan_distance(s, i) for i in range(len(self.goals))) for s in new_belief)
            new_f = new_g + min_h
            best_state = min(new_belief, key=lambda s: min(self.manhattan_distance(s, i) for i in range(len(self.goals))))
            heapq.heappush(pq, (new_f, new_g, new_belief, path + [best_state], belief_history + [new_belief.copy()]))
        return None, [], []

    def partial_observable_search(self, max_states=4, max_steps=1000):
        initial_belief = set(self.generate_fixed_belief_states())
        pq = []
        representative_state = min(initial_belief, key=lambda s: min(self.manhattan_distance(s, i) for i in range(len(self.goals))))
        initial_h = min(self.manhattan_distance(representative_state, i) for i in range(len(self.goals)))
        heapq.heappush(pq, (initial_h, 0, initial_belief, [representative_state], [initial_belief.copy()]))
        visited = {}
        steps = 0
        while pq and steps < max_steps:
            time.sleep(0.1)
            f, g, belief, path, belief_history = heapq.heappop(pq)
            belief_key = frozenset(belief)
            if belief_key in visited and visited[belief_key] <= f:
                continue
            visited[belief_key] = f
            steps += 1
            for state in belief:
                for goal in self.goals:
                    if state == goal:
                        return path, list(belief), belief_history
            observation = self.get_observation(representative_state)
            if observation is None:
                continue
            filtered_belief = set()
            for state in belief:
                if self.get_observation(state) == observation:
                    filtered_belief.add(state)
            if not filtered_belief:
                filtered_belief = belief
            new_belief = set()
            for state in filtered_belief:
                new_belief.update(self.get_neighbors(state))
            if len(new_belief) > max_states:
                new_belief = set(sorted(new_belief, key=lambda s: min(self.manhattan_distance(s, i) for i in range(len(self.goals))) + g)[:max_states])
            if not new_belief:
                continue
            new_g = g + 1
            representative_state = min(new_belief, key=lambda s: min(self.manhattan_distance(s, i) for i in range(len(self.goals))))
            min_h = min(self.manhattan_distance(representative_state, i) for i in range(len(self.goals)))
            new_f = new_g + min_h
            if random.random() < 0.1:
                representative_state = random.choice(list(new_belief))
            heapq.heappush(pq, (new_f, new_g, new_belief, path + [representative_state], belief_history + [new_belief.copy()]))
        return None, [], []

def draw_grid(screen, state, tile_size, offset_x, offset_y, font):
    BACKGROUND = (240, 240, 240)  # Light gray background
    TILE_COLOR = (34, 139, 34)    # Forest green for numbered tiles
    BLANK_COLOR = (220, 220, 220) # Light gray for blank tile
    TEXT_COLOR = (255, 255, 255)  # White text
    LINE_COLOR = (50, 50, 50)     # Dark gray lines
    pygame.draw.rect(screen, BACKGROUND, (offset_x, offset_y, tile_size * 3, tile_size * 3))
    for i in range(3):
        for j in range(3):
            x, y = offset_x + j * tile_size, offset_y + i * tile_size
            color = BLANK_COLOR if state[i][j] == 0 else TILE_COLOR
            pygame.draw.rect(screen, color, (x + 2, y + 2, tile_size - 4, tile_size - 4), border_radius=0)  # No rounded corners
            if state[i][j] != 0:
                text = font.render(str(state[i][j]), True, TEXT_COLOR)
                text_rect = text.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
                screen.blit(text, text_rect)
    for i in range(4):
        pygame.draw.line(screen, LINE_COLOR, (offset_x, offset_y + i * tile_size), (offset_x + tile_size * 3, offset_y + i * tile_size), 2)
        pygame.draw.line(screen, LINE_COLOR, (offset_x + i * tile_size, offset_y), (offset_x + i * tile_size, offset_y + tile_size * 3), 2)

def print_solution(solution, belief_states, elapsed_time, belief_history=None):
    if solution is None:
        print("Không tìm thấy đường đi đến trạng thái mục tiêu!")
        return
    print("Đường đi:")
    for step, state in enumerate(solution):
        print(f"Bước {step}:")
        for row in state:
            print(row)
        print()
    print("Các trạng thái niềm tin cuối cùng:")
    for i, state in enumerate(belief_states):
        print(f"Trạng thái niềm tin {i+1}:")
        for row in state:
            print(row)
        print()
    if belief_history:
        print(f"Số bước trong lịch sử niềm tin: {len(belief_history)}")
    print(f"Thời gian thực thi: {elapsed_time:.8f}s")
    print("Hoàn thành!")

def print_and_or_solution(solution, elapsed_time):
    if solution is None:
        print("Không tìm thấy đường đi đến trạng thái mục tiêu!")
        return
    print("Đường đi:")
    for step, state in enumerate(solution):
        print(f"Bước {step}:")
        for row in state:
            print(row)
        print()
    print(f"Thời gian thực thi: {elapsed_time:.8f}s")
    print("Hoàn thành!")

def run_and_or_window(initial_state, target_goal):
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("AND-OR Single Search")
    clock = pygame.time.Clock()

    # Fonts
    title_font = pygame.font.SysFont("Segoe UI", 24)
    label_font = pygame.font.SysFont("Segoe UI", 16)
    status_font = pygame.font.SysFont("Segoe UI", 16)

    # Colors
    BUTTON_COLOR = (70, 130, 180)  # Steel blue
    BUTTON_HOVER = (100, 149, 237) # Light blue
    TEXT_COLOR = (255, 255, 255)   # White
    BACKGROUND_GRADIENT = [(135, 206, 250), (255, 255, 255)] # Sky blue to white

    # Gradient background
    gradient_surface = pygame.Surface((600, 400))
    for y in range(400):
        t = y / 399
        color = (
            int(BACKGROUND_GRADIENT[0][0] * (1 - t) + BACKGROUND_GRADIENT[1][0] * t),
            int(BACKGROUND_GRADIENT[0][1] * (1 - t) + BACKGROUND_GRADIENT[1][1] * t),
            int(BACKGROUND_GRADIENT[0][2] * (1 - t) + BACKGROUND_GRADIENT[1][2] * t)
        )
        pygame.draw.line(gradient_surface, color, (0, y), (600, y))

    # Buttons
    buttons = [
        {"text": "Start", "rect": pygame.Rect(20, 50, 100, 30)},
        {"text": "Reset", "rect": pygame.Rect(130, 50, 100, 30)},
        {"text": "Pause/Resume", "rect": pygame.Rect(240, 50, 120, 30)},
    ]

    puzzle = EightPuzzle(initial_state, [target_goal])
    solution = []
    step = 0
    elapsed_time = None
    running = True
    animating = False
    paused = False
    last_step_time = time.time()
    status_message = "Nhấn Start để bắt đầu!"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if buttons[0]["rect"].collidepoint((x, y)) and not animating:  # Start button
                    status_message = "Đang giải với AND-OR Single Search..."
                    screen.blit(gradient_surface, (0, 0))
                    status_text = status_font.render(status_message, True, TEXT_COLOR)
                    screen.blit(status_text, (20, 350))
                    pygame.display.flip()  # Update display to show status
                    start_time = time.time()
                    solution = puzzle.and_or_search_single(target_goal, max_steps=1000)
                    elapsed_time = time.time() - start_time
                    step = 0
                    last_step_time = time.time()
                    animating = bool(solution)
                    paused = False
                    status_message = "Đang hiển thị giải pháp..." if solution else "Không tìm thấy giải pháp!"
                    print("\nKết quả của thuật toán AND-OR Single Search:")
                    print_and_or_solution(solution, elapsed_time)
                elif buttons[1]["rect"].collidepoint((x, y)):  # Reset button
                    status_message = "Đang giải với AND-OR Single Search..."
                    screen.blit(gradient_surface, (0, 0))
                    status_text = status_font.render(status_message, True, TEXT_COLOR)
                    screen.blit(status_text, (20, 350))
                    pygame.display.flip()  # Update display to show status
                    start_time = time.time()
                    solution = puzzle.and_or_search_single(target_goal, max_steps=1000)
                    elapsed_time = time.time() - start_time
                    step = 0
                    last_step_time = time.time()
                    animating = bool(solution)
                    paused = False
                    status_message = "Đang hiển thị giải pháp..." if solution else "Không tìm thấy giải pháp!"
                    print("\nKết quả của thuật toán AND-OR Single Search:")
                    print_and_or_solution(solution, elapsed_time)
                elif buttons[2]["rect"].collidepoint((x, y)):  # Pause/Resume button
                    paused = not paused
                    status_message = "Tạm dừng" if paused else "Tiếp tục"

        if not running:
            break

        screen.blit(gradient_surface, (0, 0))

        # Draw title
        title = title_font.render("AND-OR Single Search", True, TEXT_COLOR)
        screen.blit(title, (20, 10))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            color = BUTTON_HOVER if button["rect"].collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, color, button["rect"], border_radius=10)
            label = label_font.render(button["text"], True, TEXT_COLOR)
            label_rect = label.get_rect(center=button["rect"].center)
            screen.blit(label, label_rect)

        # Draw current state
        if animating and solution and step < len(solution) and not paused:
            current_state = solution[step]
            print(f"Hiển thị bước {step}: {current_state}")  # Debug: In trạng thái hiện tại
        else:
            current_state = initial_state
        state_label = label_font.render("Trạng Thái Hiện Tại", True, TEXT_COLOR)
        screen.blit(state_label, (20, 90))
        draw_grid(screen, current_state, 80, 20, 120, label_font)

        # Draw goal state
        goal_label = label_font.render("Trạng Thái Mục Tiêu", True, TEXT_COLOR)
        screen.blit(goal_label, (300, 90))
        draw_grid(screen, target_goal, 50, 300, 120, status_font)

        # Draw status and time
        status_text = status_font.render(status_message, True, TEXT_COLOR)
        screen.blit(status_text, (20, 350))
        if elapsed_time is not None:
            time_text = status_font.render(f"Thời gian: {elapsed_time:.2f} giây", True, TEXT_COLOR)
            screen.blit(time_text, (20, 370))

        # Animation logic
        if animating and solution and time.time() - last_step_time > 1.0 and not paused:
            step += 1
            last_step_time = time.time()
            print(f"Tăng step lên {step}, animating={animating}, len(solution)={len(solution)}")  # Debug
            if step >= len(solution):
                animating = False
                step = len(solution) - 1 if solution else 0
                status_message = "Hoàn thành!"
                print("Hoàn thành hiển thị")  # Debug

        pygame.display.flip()
        clock.tick(60)

    pygame.display.quit()

def run_and_or_process(initial_state, target_goal):
    process = multiprocessing.Process(target=run_and_or_window, args=(initial_state, target_goal))
    process.start()

async def run_pygame():
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("8-Puzzle Solver")
    clock = pygame.time.Clock()

    # Fonts
    title_font = pygame.font.SysFont("Segoe UI", 32)
    label_font = pygame.font.SysFont("Segoe UI", 20)
    status_font = pygame.font.SysFont("Segoe UI", 20)

    # Colors
    BUTTON_COLOR = (70, 130, 180)  # Steel blue
    BUTTON_HOVER = (100, 149, 237) # Light blue
    TEXT_COLOR = (255, 255, 255)   # White
    BACKGROUND_GRADIENT = [(135, 206, 250), (255, 255, 255)] # Sky blue to white

    # Gradient background
    gradient_surface = pygame.Surface((1200, 800))
    for y in range(800):
        t = y / 799
        color = (
            int(BACKGROUND_GRADIENT[0][0] * (1 - t) + BACKGROUND_GRADIENT[1][0] * t),
            int(BACKGROUND_GRADIENT[0][1] * (1 - t) + BACKGROUND_GRADIENT[1][1] * t),
            int(BACKGROUND_GRADIENT[0][2] * (1 - t) + BACKGROUND_GRADIENT[1][2] * t)
        )
        pygame.draw.line(gradient_surface, color, (0, y), (1200, y))

    # Initial and goal states
    initial_state = [[1, 0, 3], [4, 2, 6], [7, 5, 8]]  # Easier initial state
    goal_states = [
        [[1, 2, 3], [4, 5, 6], [7, 8, 0]],
        [[1, 2, 3], [4, 5, 6], [0, 7, 8]],
        [[1, 2, 3], [0, 4, 6], [7, 5, 8]]
    ]
    target_goal = tuple(map(tuple, [[1, 2, 3], [4, 5, 6], [7, 8, 0]]))
    puzzle = EightPuzzle(initial_state, goal_states)

    # Buttons
    buttons = [
        {"text": "Sensorless", "rect": pygame.Rect(20, 50, 200, 40)},
        {"text": "Partial Observable Search", "rect": pygame.Rect(230, 50, 250, 40)},
        {"text": "AND-OR Single Search", "rect": pygame.Rect(490, 50, 200, 40)},
        {"text": "Reset", "rect": pygame.Rect(700, 50, 150, 40)},
        {"text": "Pause/Resume", "rect": pygame.Rect(860, 50, 150, 40)},
    ]

    belief_states = puzzle.generate_fixed_belief_states()
    belief_history = []
    solution = []
    step = 0
    elapsed_time = None
    running = True
    animating = False
    paused = False
    last_step_time = time.time()
    status_message = "Chọn thuật toán để giải!"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if buttons[0]["rect"].collidepoint((x, y)) and not animating:
                    status_message = "Đang giải với Sensorless..."
                    start_time = time.time()
                    solution, belief_states, belief_history = puzzle.belief_state_search(max_states=4)
                    elapsed_time = time.time() - start_time
                    step = 0
                    last_step_time = time.time()
                    animating = True
                    paused = False
                    status_message = "Đang hiển thị giải pháp..." if solution else "Không tìm thấy giải pháp!"
                    print("\nKết quả của thuật toán Sensorless:")
                    print_solution(solution, belief_states, elapsed_time, belief_history)
                    await asyncio.sleep(0.5)
                elif buttons[1]["rect"].collidepoint((x, y)) and not animating:
                    status_message = "Đang giải với Partial Observable Search..."
                    start_time = time.time()
                    solution, belief_states, belief_history = puzzle.partial_observable_search(max_states=4)
                    elapsed_time = time.time() - start_time
                    step = 0
                    last_step_time = time.time()
                    animating = True
                    paused = False
                    status_message = "Đang hiển thị giải pháp..." if solution else "Không tìm thấy giải pháp!"
                    print("\nKết quả của thuật toán Partial Observable Search:")
                    print_solution(solution, belief_states, elapsed_time, belief_history)
                    await asyncio.sleep(0.5)
                elif buttons[2]["rect"].collidepoint((x, y)) and not animating:
                    status_message = "Mở cửa sổ AND-OR Single Search..."
                    run_and_or_process(initial_state, target_goal)
                    status_message = "Chọn thuật toán để giải!"
                elif buttons[3]["rect"].collidepoint((x, y)):
                    solution = []
                    belief_states = puzzle.generate_fixed_belief_states()
                    belief_history = []
                    step = 0
                    elapsed_time = None
                    animating = False
                    paused = False
                    status_message = "Đã đặt lại trạng thái!"
                elif buttons[4]["rect"].collidepoint((x, y)):
                    paused = not paused
                    status_message = "Tạm dừng" if paused else "Tiếp tục"

        if not running:
            break

        screen.blit(gradient_surface, (0, 0))

        # Draw title
        title = title_font.render("8-Puzzle Solver", True, TEXT_COLOR)
        screen.blit(title, (20, 10))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            color = BUTTON_HOVER if button["rect"].collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, color, button["rect"], border_radius=10)
            label = label_font.render(button["text"], True, TEXT_COLOR)
            label_rect = label.get_rect(center=button["rect"].center)
            screen.blit(label, label_rect)

        # Draw belief states
        if belief_history and (animating or step > 0) and not paused:
            current_beliefs = list(belief_history[min(step, len(belief_history) - 1)])
        else:
            current_beliefs = belief_states
        for i in range(min(4, len(current_beliefs))):
            belief_label = label_font.render(f"Trạng Thái Niềm Tin {i+1}", True, TEXT_COLOR)
            screen.blit(belief_label, (20 + i * 300, 100))
            draw_grid(screen, current_beliefs[i], 80, 20 + i * 300, 140, label_font)

        # Draw goal states
        for i in range(3):
            goal_label = label_font.render(f"Trạng Thái Mục Tiêu {i+1}", True, TEXT_COLOR)
            screen.blit(goal_label, (20 + i * 300, 400))
            draw_grid(screen, puzzle.goals[i], 80, 20 + i * 300, 440, label_font)

        # Draw status and time
        status_text = status_font.render(status_message, True, TEXT_COLOR)
        screen.blit(status_text, (20, 700))
        if elapsed_time is not None:
            time_text = status_font.render(f"Thời gian: {elapsed_time:.2f} giây", True, TEXT_COLOR)
            screen.blit(time_text, (20, 730))

        # Animation logic
        if animating and time.time() - last_step_time > 1.0 and not paused:
            step += 1
            last_step_time = time.time()
            if step >= len(belief_history):
                animating = False
                step = len(belief_history) - 1
                status_message = "Hoàn thành!"

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    if platform.system() == "Emscripten":
        asyncio.ensure_future(run_pygame())
    else:
        asyncio.run(run_pygame())