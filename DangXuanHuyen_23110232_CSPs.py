import pygame
import time
import random
from collections import defaultdict
import uuid

class EightPuzzle:
    def __init__(self, initial, goal):
        # Khởi tạo trạng thái ban đầu và mục tiêu
        # Chuyển danh sách thành tuple để đảm bảo không thay đổi
        self.initial = tuple(map(tuple, initial))
        self.goal = tuple(map(tuple, goal))

    def is_valid_assignment(self, state, pos, value):
        # Kiểm tra xem giá trị có thể gán vào vị trí (i, j) trong trạng thái hiện tại
        i, j = pos
        # Kiểm tra trùng giá trị (trừ ô đang xét)
        for r in range(3):
            for c in range(3):
                if (r, c) != pos and state[r][c] == value:
                    return False
        # Kiểm tra ràng buộc hàng ngang và dọc
        # Ô bên trái phải nhỏ hơn 1 nếu không phải ô trống
        if j > 0 and state[i][j - 1] != 0 and value != 0 and state[i][j - 1] != value - 1:
            return False
        # Ô bên phải phải lớn hơn 1 nếu không phải ô trống
        if j < 2 and value != 0 and state[i][j + 1] != 0 and state[i][j + 1] != value + 1:
            return False
        # Ô phía trên phải nhỏ hơn 3 nếu không phải ô trống
        if i > 0 and state[i - 1][j] != 0 and value != 0 and state[i - 1][j] != value - 3:
            return False
        # Ô phía dưới phải lớn hơn 3 nếu không phải ô trống
        if i < 2 and value != 0 and state[i + 1][j] != 0 and state[i + 1][j] != value + 3:
            return False
        return True

    def is_solvable(self, state):
        # Kiểm tra xem trạng thái có thể giải được
        # Đếm số lần đảo ngược trong danh sách các số (trừ ô trống)
        flat = [state[i][j] for i in range(3) for j in range(3) if state[i][j] != 0]
        inversions = 0
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] > flat[j]:
                    inversions += 1
        # Trạng thái có thể giải được nếu số đảo ngược là chẵn
        return inversions % 2 == 0

    def count_conflicts(self, state):
        # Đếm số xung đột trong trạng thái
        conflicts = 0
        value_counts = defaultdict(int)
        # Đếm số lần xuất hiện của mỗi giá trị (trừ 0)
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                if val != 0:
                    value_counts[val] += 1
                    if value_counts[val] > 1:
                        conflicts += 2 * (value_counts[val] - 1)
        # Kiểm tra xung đột hàng ngang
        for i in range(3):
            for j in range(2):
                if state[i][j] != 0 and state[i][j + 1] != 0:
                    if state[i][j + 1] != state[i][j] + 1:
                        conflicts += 1
        # Kiểm tra xung đột hàng dọc
        for j in range(3):
            for i in range(2):
                if state[i][j] != 0 and state[i + 1][j] != 0:
                    if state[i + 1][j] != state[i][j] + 3:
                        conflicts += 1
        # Thêm xung đột nếu trạng thái không thể giải
        if not self.is_solvable(state):
            conflicts += 10
        return conflicts

    def backtracking_search(self):
        # Tìm lời giải bằng thuật toán Backtracking
        visited = set()  # Lưu các trạng thái đã xét
        path = []  # Lưu đường đi
        def backtrack(state, assigned, pos_index):
            # Nếu đã gán hết 9 ô
            if pos_index == 9:
                state_tuple = tuple(tuple(row) for row in state)
                # Kiểm tra trạng thái có phải mục tiêu và có thể giải
                if state_tuple == self.goal and self.is_solvable(state):
                    path.append(state_tuple)
                    return path
                return None
            i, j = divmod(pos_index, 3)  # Tính vị trí (i, j)
            state_tuple = tuple(tuple(row) for row in state)
            # Nếu trạng thái đã xét, bỏ qua
            if state_tuple in visited:
                return None
            visited.add(state_tuple)
            path.append(state_tuple)
            # Thử gán các giá trị từ 0 đến 8
            for value in [1, 2, 3, 4, 5, 6, 7, 8, 0]:
                if value not in assigned:
                    if self.is_valid_assignment(state, (i, j), value):
                        new_state = [row[:] for row in state]
                        new_state[i][j] = value
                        new_assigned = assigned | {value}
                        result = backtrack(new_state, new_assigned, pos_index + 1)
                        if result is not None:
                            return result
            path.pop()
            return None
        empty_state = [[0 for _ in range(3)] for _ in range(3)]
        result = backtrack(empty_state, set(), 0)
        return result

    def forward_checking_search(self):
        # Tìm lời giải bằng thuật toán Forward Checking
        visited = set()
        path = []
        def get_domain(state, pos, assigned):
            # Lấy danh sách giá trị có thể gán cho vị trí (i, j)
            i, j = pos
            domain = []
            for value in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
                if value not in assigned and self.is_valid_assignment(state, (i, j), value):
                    domain.append(value)
            return domain
        def forward_check(state, pos, value, domains, assigned):
            # Cập nhật danh sách giá trị khả thi sau khi gán
            i, j = pos
            new_domains = {k: v[:] for k, v in domains.items()}
            success = True
            for r in range(3):
                for c in range(3):
                    if (r, c) not in assigned and (r, c) != pos:
                        if (r, c) in new_domains:
                            new_domain = new_domains[(r, c)][:]
                            if value != 0 and value in new_domain:
                                if r == i:
                                    if c < j and value - 1 in new_domain:
                                        new_domain = [v for v in new_domain if v == 0 or v == value - 1]
                                    elif c > j and value + 1 in new_domain:
                                        new_domain = [v for v in new_domain if v == 0 or v == value + 1]
                                if c == j:
                                    if r < i and value - 3 in new_domain:
                                        new_domain = [v for v in new_domain if v == 0 or v == value - 3]
                                    elif r > i and value + 3 in new_domain:
                                        new_domain = [v for v in new_domain if v == 0 or v == value + 3]
                                if value in new_domain:
                                    new_domain.remove(value)
                            new_domains[(r, c)] = new_domain
                            if not new_domain:
                                success = False
            return success, new_domains
        def select_mrv_variable(positions, domains):
            # Chọn biến có số giá trị khả thi ít nhất
            min_domain_size = float('inf')
            selected_pos = None
            for pos in positions:
                if pos in domains:
                    domain_size = len(domains[pos])
                    if domain_size < min_domain_size:
                        min_domain_size = domain_size
                        selected_pos = pos
            return selected_pos
        def select_lcv_value(pos, domain, state, domains, assigned):
            # Sắp xếp giá trị theo thứ tự ít gây xung đột nhất
            value_scores = []
            for value in domain:
                temp_state = [row[:] for row in state]
                temp_state[pos[0]][pos[1]] = value
                _, new_domains = forward_check(temp_state, pos, value, domains, assigned)
                remaining = sum(len(new_domains[p]) for p in new_domains if p != pos)
                if value == self.goal[pos[0]][pos[1]]:
                    remaining += 10
                value_scores.append((-remaining, value))
            value_scores.sort()
            return [value for _, value in value_scores]
        def backtrack_with_fc(state, assigned, positions, domains):
            # Hàm đệ quy với Forward Checking
            if len(assigned) == 9:
                state_tuple = tuple(tuple(row) for row in state)
                if state_tuple == self.goal and self.is_solvable(state):
                    path.append(state_tuple)
                    return path
                return None
            pos = select_mrv_variable(positions, domains)
            if pos is None:
                return None
            domain = get_domain(state, pos, set(assigned.values()))
            if not domain:
                return None
            sorted_values = select_lcv_value(pos, domain, state, domains, assigned)
            state_tuple = tuple(tuple(row) for row in state)
            if state_tuple in visited:
                return None
            visited.add(state_tuple)
            path.append(state_tuple)
            for value in sorted_values:
                new_state = [row[:] for row in state]
                new_state[pos[0]][pos[1]] = value
                new_assigned = assigned.copy()
                new_assigned[pos] = value
                new_positions = [p for p in positions if p != pos]
                success, new_domains = forward_check(new_state, pos, value, domains, new_assigned)
                if success:
                    result = backtrack_with_fc(new_state, new_assigned, new_positions, new_domains)
                    if result is not None:
                        return result
                new_domains.pop(pos, None)
            path.pop()
            return None
        empty_state = [[0 for _ in range(3)] for _ in range(3)]
        positions = [(i, j) for i in range(3) for j in range(3)]
        domains = {(i, j): [0, 1, 2, 3, 4, 5, 6, 7, 8] for i in range(3) for j in range(3)}
        assigned = {}
        result = backtrack_with_fc(empty_state, assigned, positions, domains)
        return result

    def min_conflicts_search(self, max_steps=1000):
        # Tìm lời giải bằng thuật toán Min-Conflicts
        def find_blank(state):
            # Tìm vị trí ô trống
            for i in range(3):
                for j in range(3):
                    if state[i][j] == 0:
                        return i, j
            return None
        def get_neighbors(i, j):
            # Lấy danh sách các ô láng giềng
            neighbors = []
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < 3 and 0 <= nj < 3:
                    neighbors.append((ni, nj))
            return neighbors
        def count_conflicts(state):
            # Đếm số xung đột dựa trên khoảng cách tới vị trí mục tiêu
            conflicts = 0
            goal_positions = {self.goal[i][j]: (i, j) for i in range(3) for j in range(3) if self.goal[i][j] != 0}
            for i in range(3):
                for j in range(3):
                    if state[i][j] != 0:
                        goal_i, goal_j = goal_positions.get(state[i][j], (i, j))
                        conflicts += abs(i - goal_i) + abs(j - goal_j)
            return conflicts
        def is_valid_state(state):
            # Kiểm tra trạng thái hợp lệ (có đủ số từ 0-8)
            flat = [state[i][j] for i in range(3) for j in range(3)]
            return sorted(flat) == [0, 1, 2, 3, 4, 5, 6, 7, 8]
        # Khởi tạo trạng thái ban đầu
        if is_valid_state(self.initial) and self.is_solvable(self.initial):
            current_state = [row[:] for row in self.initial]
        else:
            numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8]
            random.shuffle(numbers)
            current_state = [[0 for _ in range(3)] for _ in range(3)]
            idx = 0
            for i in range(3):
                for j in range(3):
                    current_state[i][j] = numbers[idx]
                    idx += 1
            while not self.is_solvable(current_state):
                random.shuffle(numbers)
                idx = 0
                for i in range(3):
                    for j in range(3):
                        current_state[i][j] = numbers[idx]
                        idx += 1
        path = [tuple(tuple(row) for row in current_state)]
        steps = 0
        visited = set([tuple(tuple(row) for row in current_state)])
        while steps < max_steps:
            current_state_tuple = tuple(tuple(row) for row in current_state)
            if current_state_tuple == self.goal:
                print(f"Đã tìm thấy lời giải sau {steps} bước")
                return path
            blank_i, blank_j = find_blank(current_state)
            if blank_i is None:
                print("Trạng thái không hợp lệ: Không tìm thấy ô trống")
                return None
            neighbors = get_neighbors(blank_i, blank_j)
            if not neighbors:
                print("Không có nước đi hợp lệ")
                return None
            best_conflicts = float('inf')
            best_states = []
            for ni, nj in neighbors:
                temp_state = [row[:] for row in current_state]
                temp_state[blank_i][blank_j], temp_state[ni][nj] = temp_state[ni][nj], temp_state[blank_i][blank_j]
                temp_state_tuple = tuple(tuple(row) for row in temp_state)
                if temp_state_tuple in visited:
                    continue
                conflicts = count_conflicts(temp_state)
                if conflicts < best_conflicts:
                    best_conflicts = conflicts
                    best_states = [(temp_state, (ni, nj))]
                elif conflicts == best_conflicts:
                    best_states.append((temp_state, (ni, nj)))
            if not best_states:
                ni, nj = random.choice(neighbors)
                temp_state = [row[:] for row in current_state]
                temp_state[blank_i][blank_j], temp_state[ni][nj] = temp_state[ni][nj], temp_state[blank_i][blank_j]
                best_states = [(temp_state, (ni, nj))]
            best_state, _ = random.choice(best_states)
            current_state = best_state
            current_state_tuple = tuple(tuple(row) for row in current_state)
            visited.add(current_state_tuple)
            path.append(current_state_tuple)
            steps += 1
        print("Không tìm thấy lời giải trong giới hạn bước")
        return None

def draw_grid(screen, state, tile_size, offset_x, offset_y, font):
    # Hàm vẽ lưới 3x3 của trò chơi
    BACKGROUND = (240, 240, 240)  # Màu nền
    TILE_COLOR = (129, 199, 132)  # Màu ô số
    BLANK_COLOR = (239, 83, 80)  # Màu ô trống
    TEXT_COLOR = (255, 255, 255)  # Màu chữ
    LINE_COLOR = (50, 50, 50)  # Màu đường kẻ
    # Vẽ nền cho lưới
    pygame.draw.rect(screen, BACKGROUND, (offset_x, offset_y, 300, 300))
    # Vẽ từng ô
    for i in range(3):
        for j in range(3):
            x, y = offset_x + j * tile_size, offset_y + i * tile_size
            color = BLANK_COLOR if state[i][j] == 0 else TILE_COLOR
            # Vẽ hình chữ nhật cho ô, không có bo góc
            pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))
            if state[i][j] != 0:
                # Vẽ số lên ô
                text = font.render(str(state[i][j]), True, TEXT_COLOR)
                text_rect = text.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
                screen.blit(text, text_rect)
    # Vẽ các đường kẻ chia ô
    for i in range(4):
        pygame.draw.line(screen, LINE_COLOR, (offset_x, offset_y + i * tile_size), (offset_x + 300, offset_y + i * tile_size), 2)
        pygame.draw.line(screen, LINE_COLOR, (offset_x + i * tile_size, offset_y), (offset_x + i * tile_size, offset_y + 300), 2)

def print_solution(solution):
    # In các bước của lời giải
    if solution is None or len(solution) == 0:
        print("Không tìm thấy đường đi đến trạng thái mục tiêu!")
        return
    for step, state in enumerate(solution):
        print(f"Bước {step}:")
        for row in state:
            print(row)
        print()
    print("Hoàn thành!")

def run_pygame(puzzle):
    # Hàm chạy giao diện Pygame
    pygame.init()
    screen = pygame.display.set_mode((700, 500))  # Tạo cửa sổ 700x500
    pygame.display.set_caption("8-Puzzle Solver")  # Đặt tiêu đề
    clock = pygame.time.Clock()  # Quản lý tốc độ khung hình
    title_font = pygame.font.Font(None, 48)  # Font cho tiêu đề
    button_font = pygame.font.Font(None, 36)  # Font cho nút
    status_font = pygame.font.Font(None, 32)  # Font cho trạng thái
    BUTTON_COLOR = (70, 130, 180)  # Màu nút
    BUTTON_HOVER = (100, 149, 237)  # Màu nút khi hover
    TEXT_COLOR = (255, 255, 255)  # Màu chữ
    BACKGROUND_GRADIENT = [(135, 206, 250), (255, 255, 255)]  # Gradient nền
    # Tạo gradient cho nền
    gradient_surface = pygame.Surface((700, 500))
    for y in range(500):
        t = y / 499
        color = (
            int(BACKGROUND_GRADIENT[0][0] * (1 - t) + BACKGROUND_GRADIENT[1][0] * t),
            int(BACKGROUND_GRADIENT[0][1] * (1 - t) + BACKGROUND_GRADIENT[1][1] * t),
            int(BACKGROUND_GRADIENT[0][2] * (1 - t) + BACKGROUND_GRADIENT[1][2] * t)
        )
        pygame.draw.line(gradient_surface, color, (0, y), (700, y))
    # Danh sách các nút
    buttons = [
        {"text": "Backtracking", "rect": pygame.Rect(30, 100, 200, 50)},
        {"text": "Forward Checking", "rect": pygame.Rect(30, 170, 200, 50)},
        {"text": "Min-Conflicts", "rect": pygame.Rect(30, 240, 200, 50)},
        {"text": "Reset", "rect": pygame.Rect(30, 310, 200, 50)},
        {"text": "Pause/Resume", "rect": pygame.Rect(30, 380, 200, 50)},
    ]
    running = True
    solution = None
    step = 0
    elapsed_time = None
    algorithm_run = False
    paused = False
    status_message = ""
    while running:
        # Vẽ nền gradient
        screen.blit(gradient_surface, (0, 0))
        # Vẽ tiêu đề
        title = title_font.render("8-Puzzle Solver", True, TEXT_COLOR)
        screen.blit(title, (250, 20))
        # Vẽ hướng dẫn
        guide = status_font.render("Chọn thuật toán để giải!", True, TEXT_COLOR)
        screen.blit(guide, (250, 60))
        # Xử lý hover cho nút
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            color = BUTTON_HOVER if button["rect"].collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, color, button["rect"], border_radius=10)
            label = button_font.render(button["text"], True, TEXT_COLOR)
            label_rect = label.get_rect(center=button["rect"].center)
            screen.blit(label, label_rect)
        # Hiển thị lưới
        if solution and algorithm_run and step < len(solution) and not paused:
            draw_grid(screen, solution[step], 100, 350, 100, button_font)
            if step < len(solution) - 1:
                step += 1
                time.sleep(0.1)
        else:
            draw_grid(screen, puzzle.initial, 100, 350, 100, button_font)
        # Hiển thị thông báo trạng thái
        if status_message:
            status_text = status_font.render(status_message, True, TEXT_COLOR)
            screen.blit(status_text, (350, 420))
        # Hiển thị thời gian chạy
        if elapsed_time is not None:
            time_text = status_font.render(f"Thời gian: {elapsed_time:.2f} giây", True, TEXT_COLOR)
            screen.blit(time_text, (350, 450))
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not algorithm_run or event.type == pygame.MOUSEBUTTONDOWN and buttons[4]["rect"].collidepoint(event.pos):
                x, y = event.pos
                start_time = time.time()
                if buttons[0]["rect"].collidepoint((x, y)) and not algorithm_run:
                    status_message = "Đang giải với Backtracking..."
                    solution = puzzle.backtracking_search()
                    step = 0
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    status_message = "Hoàn thành!" if solution else "Không tìm thấy giải pháp!"
                    print("\nKết quả của thuật toán Backtracking:")
                    print_solution(solution)
                    print(f"Thời gian thực thi: {elapsed_time:.2f} giây")
                    algorithm_run = True
                elif buttons[1]["rect"].collidepoint((x, y)) and not algorithm_run:
                    status_message = "Đang giải với Forward Checking..."
                    solution = puzzle.forward_checking_search()
                    step = 0
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    status_message = "Hoàn thành!" if solution else "Không tìm thấy giải pháp!"
                    print("\nKết quả của thuật toán Forward Checking:")
                    print_solution(solution)
                    print(f"Thời gian thực thi: {elapsed_time:.2f} giây")
                    algorithm_run = True
                elif buttons[2]["rect"].collidepoint((x, y)) and not algorithm_run:
                    status_message = "Đang giải với Min-Conflicts..."
                    solution = puzzle.min_conflicts_search()
                    step = 0
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    status_message = "Hoàn thành!" if solution else "Không tìm thấy giải pháp!"
                    print("\nKết quả của thuật toán Min-Conflicts:")
                    print_solution(solution)
                    print(f"Thời gian thực thi: {elapsed_time:.2f} giây")
                    algorithm_run = True
                elif buttons[3]["rect"].collidepoint((x, y)):
                    solution = None
                    step = 0
                    elapsed_time = None
                    algorithm_run = False
                    paused = False
                    puzzle = EightPuzzle(initial_state, goal_state)
                    status_message = "Đã đặt lại trạng thái!"
                elif buttons[4]["rect"].collidepoint((x, y)):
                    paused = not paused
                    status_message = "Tạm dừng" if paused else "Tiếp tục"
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    # Trạng thái ban đầu và mục tiêu
    initial_state = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    puzzle = EightPuzzle(initial_state, goal_state)
    run_pygame(puzzle)