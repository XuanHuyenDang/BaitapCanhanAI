import pygame
import sys
import time
import random
from collections import defaultdict
from typing import Tuple, Dict, Set, List

# ----------- Phần giải thuật Q-learning ------------
State = Tuple[int, ...]
Action = str
GOAL: State = (1, 2, 3, 4, 5, 6, 7, 8, 0)  # Trạng thái đích

# Hàm sinh các trạng thái kế tiếp từ trạng thái hiện tại
def ke(x: State) -> List[Tuple[Action, State]]:
    neighbors = []
    z = x.index(0)
    r, c = divmod(z, 3)
    moves = [(1, 0, 'D'), (-1, 0, 'U'), (0, 1, 'R'), (0, -1, 'L')]
    for dr, dc, move in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            y = list(x)
            nz = nr * 3 + nc
            y[z], y[nz] = y[nz], y[z]
            neighbors.append((move, tuple(y)))
    return neighbors

# Thuật toán Q-learning
def q_learning(start_node: State, goal_node: State = GOAL, episodes: int = 10000) -> Tuple[str, float]:
    alpha, gamma = 0.1, 0.9  # Tốc độ học và hệ số giảm
    epsilon, epsilon_end, decay = 1.0, 0.01, 0.999
    max_steps = 200
    q_table: Dict[State, Dict[Action, float]] = defaultdict(lambda: defaultdict(float))
    start_time = time.perf_counter()

    # Huấn luyện Q-learning
    for episode in range(episodes):
        current_state = start_node
        for _ in range(max_steps):
            if current_state == goal_node:
                break
            valid_moves = ke(current_state)
            if random.random() < epsilon:
                action, next_state = random.choice(valid_moves)
            else:
                q_vals = [(move, q_table[current_state][move]) for move, _ in valid_moves]
                max_q = max([q for _, q in q_vals], default=0)
                best = [mv for mv, q in q_vals if q == max_q]
                action = random.choice(best) if best else valid_moves[0][0]
                next_state = dict(valid_moves)[action]
            reward = 100 if next_state == goal_node else -1
            max_next_q = max([q_table[next_state][m] for m, _ in ke(next_state)], default=0)
            q_table[current_state][action] += alpha * (reward + gamma * max_next_q - q_table[current_state][action])
            current_state = next_state
        if epsilon > epsilon_end:
            epsilon *= decay

    # Trích xuất đường đi tốt nhất sau khi huấn luyện
    path = ""
    current_state = start_node
    visited = {current_state}
    for _ in range(100):
        if current_state == goal_node:
            break
        valid_moves = ke(current_state)
        q_vals = [(move, q_table[current_state][move]) for move, _ in valid_moves]
        if not q_vals:
            break
        max_q = max([q for _, q in q_vals])
        best_moves = [mv for mv, q in q_vals if q == max_q]
        move = random.choice(best_moves)
        next_state = dict(valid_moves)[move]
        if next_state in visited:
            break
        path += move
        visited.add(next_state)
        current_state = next_state

    return path, time.perf_counter() - start_time

# ----------- Giao diện Pygame ----------------

# Cài đặt giao diện
TILE_SIZE = 100
MARGIN = 5
WIDTH = HEIGHT = TILE_SIZE * 3 + MARGIN * 4 + 80  # Thêm khoảng cho nút
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 205, 50)
GREEN = (0, 200, 0)

# Vẽ bàn cờ 3x3
def draw_board(screen, state: State):
    screen.fill(WHITE)
    for i, val in enumerate(state):
        r, c = divmod(i, 3)
        rect = pygame.Rect(
            MARGIN + c * (TILE_SIZE + MARGIN),
            MARGIN + r * (TILE_SIZE + MARGIN),
            TILE_SIZE,
            TILE_SIZE
        )
        pygame.draw.rect(screen, BLUE if val != 0 else WHITE, rect)
        if val != 0:
            font = pygame.font.Font(None, 72)
            text = font.render(str(val), True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

# Vẽ nút "Start"
def draw_start_button(screen):
    button_rect = pygame.Rect(50, HEIGHT - 70, 100, 50)
    pygame.draw.rect(screen, GREEN, button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render("Start", True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)
    return button_rect

# Vẽ nút "Chạy lại"
def draw_rerun_button(screen):
    button_rect = pygame.Rect(160, HEIGHT - 70, 100, 50)
    pygame.draw.rect(screen, GREEN, button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render("Chạy lại", True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)
    return button_rect

# Hàm thực hiện di chuyển theo chuỗi `path`
def apply_move(state: State, move: str) -> State:
    for m, next_state in ke(state):
        if m == move:
            return next_state
    return state

# Hiển thị hoạt ảnh lời giải
def animate_solution(screen, start_state: State, path: str):
    current_state = start_state
    draw_board(screen, current_state)
    draw_start_button(screen)
    draw_rerun_button(screen)
    pygame.display.flip()
    time.sleep(1)

    for move in path:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_state = apply_move(current_state, move)
        draw_board(screen, current_state)
        draw_start_button(screen)
        draw_rerun_button(screen)
        pygame.display.flip()
        time.sleep(0.5)

# ----------- Chạy ứng dụng chính ---------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("8 Puzzle - Q-Learning")
    clock = pygame.time.Clock()
    start_state = (2, 6, 5, 1, 3, 8, 4, 7, 0)
    path = None  # Lưu trữ đường đi từ Q-learning
    has_run = False  # Kiểm tra xem đã chạy Q-learning chưa

    running = True
    # Vẽ trạng thái ban đầu
    draw_board(screen, start_state)
    draw_start_button(screen)
    draw_rerun_button(screen)
    pygame.display.flip()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Xử lý nhấn nút "Start"
                if draw_start_button(screen).collidepoint(event.pos):
                    path, _ = q_learning(start_state)  # Chạy Q-learning
                    has_run = True
                    animate_solution(screen, start_state, path)
                # Xử lý nhấn nút "Chạy lại"
                if draw_rerun_button(screen).collidepoint(event.pos) and has_run and path:
                    animate_solution(screen, start_state, path)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()