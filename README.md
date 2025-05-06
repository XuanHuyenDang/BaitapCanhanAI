# Bài tập Cá nhân AI
## Đặng Xuân Huyền - 23110232
### 1. Mục tiêu: 
Trong đồ án cá nhân, các nhóm thuật toán tìm kiếm trong Trí tuệ nhân tạo được nghiên cứu và áp dụng nhằm giải quyết bài toán 8-puzzle – một bài toán cổ điển thể hiện rõ đặc trưng của việc tìm kiếm lời giải trong không gian trạng thái. Cụ thể, đề tài tập trung vào 6 nhóm thuật toán chính: 
- Thuật toán tìm kiếm không có thông tin (Uninformed Search) như BFS, DFS, IDS và UCS, giúp khảo sát khả năng tìm lời giải khi không có thông tin định hướng; 
- Thuật toán tìm kiếm có thông tin (Informed Search) như A*, IDA* và Greedy Best-First Search, sử dụng heuristic để tối ưu hóa hiệu quả tìm kiếm; 
- Tìm kiếm cục bộ (Local Search) như Hill Climbing, Steepest Ascent Hill Climbing, Simple Hill Climbing Simulated Annealing, Stochastic Hill Climbing và Beam Search tập trung vào việc cải thiện nghiệm cục bộ mà không cần duy trì toàn bộ không gian trạng thái; 
- Tìm kiếm trong môi trường phức tạp (Searching in Complex Environments) như AND-OR Graph Search, Searching for a partially observation, Sensorless mở rộng khả năng ứng dụng sang các bài toán có tính động và không chắc chắn, định hướng cho các nghiên cứu nâng cao; 
- Bài toán thỏa mãn ràng buộc (Constraint Satisfaction Problems - CSP) như Min-conflicts search, Forward-Checking, Backtracking nhằm khảo sát khả năng biểu diễn 8-puzzle dưới dạng hệ thống ràng buộc logic; 
- Cuối cùng là học tăng cường (Reinforcement Learning), cụ thể là thuật toán Q-learning, cho phép tác nhân học cách giải quyết bài toán thông qua việc tương tác với môi trường.
Việc triển khai và so sánh các nhóm thuật toán này không chỉ giúp đánh giá hiệu quả của từng phương pháp mà còn mở ra các hướng tiếp cận đa dạng, góp phần làm phong phú thêm ứng dụng của Trí tuệ nhân tạo trong giải quyết các bài toán tìm kiếm.
### 2. Nội dung
#### *2.1. Uninformed Search Algorithms*
Một bài toán tìm kiếm trong trí tuệ nhân tạo thường bao gồm các thành phần chính sau:
- Không gian trạng thái (State space): Tập hợp tất cả các trạng thái có thể có của bài toán.
- Trạng thái khởi đầu (Initial state): Trạng thái bắt đầu của bài toán.
- Trạng thái đích (Goal state): Trạng thái hoặc tập các trạng thái mà ta muốn tìm đến.
- Hàm chuyển đổi (Transition function): Các phép biến đổi từ trạng thái này sang trạng thái khác.
- Hàm kiểm tra trạng thái đích (Goal test): Kiểm tra xem trạng thái hiện tại có phải là trạng thái đích không.
- Chi phí (Cost function): Chi phí để đi từ trạng thái này sang trạng thái khác (nếu có).

Solution (giải pháp) là một chuỗi các hành động hoặc trạng thái từ trạng thái khởi đầu đến trạng thái đích thỏa mãn bài toán tìm kiếm. Nó là kết quả cuối cùng mà thuật toán tìm kiếm trả về khi tìm được đường đi hoặc phương án thỏa mãn điều kiện mục tiêu
![Uninformed Search Algorithms](UninformedSearchAlgorithms.gif)
#### *Nhận xét:*
- DFS (Depth-First Search): Duyệt sâu vào nhánh trước, tốn ít bộ nhớ nhưng dễ rơi vào vòng lặp vô hạn và không đảm bảo tìm giải pháp tối ưu; không phù hợp cho không gian trạng thái lớn như 8-puzzle.
- BFS (Breadth-First Search): Đảm bảo tìm được giải pháp ngắn nhất nhưng tốn rất nhiều bộ nhớ và thời gian khi không gian trạng thái lớn, dễ bị bùng nổ tổ hợp trong 8-puzzle.
- UCS (Uniform-Cost Search): Tương tự BFS nhưng xét chi phí đường đi, đảm bảo tìm giải pháp tối ưu theo chi phí, tuy nhiên cũng rất tốn bộ nhớ và thời gian trong bài toán 8-puzzle.
- IDS (Iterative Deepening Search): Kết hợp ưu điểm của DFS và BFS, tiết kiệm bộ nhớ hơn BFS, tránh vòng lặp của DFS, nhưng thường chậm hơn do phải lặp lại tìm kiếm nhiều lần; vẫn chưa hiệu quả bằng các thuật toán heuristic trong 8-puzzle.
- *Tóm lại,* các thuật toán không thông tin này đều có hạn chế về hiệu suất khi áp dụng cho bài toán 8-puzzle do không sử dụng thông tin hướng dẫn, dẫn đến tốn nhiều thời gian và bộ nhớ
#### *2.2. Informed Search Algorithms*
Một bài toán tìm kiếm thường bao gồm các thành phần cơ bản sau:
- Trạng thái ban đầu (Initial state): Trạng thái xuất phát của bài toán.
- Trạng thái đích (Goal state): Trạng thái hoặc tập trạng thái mà ta cần tìm đến.
- Hành động (Actions): Các phép biến đổi để chuyển từ trạng thái này sang trạng thái khác.
- Hàm chi phí (Cost function): Chi phí thực hiện mỗi hành động hoặc di chuyển giữa các trạng thái.
- Hàm kiểm tra trạng thái đích (Goal test): Kiểm tra xem trạng thái hiện tại có phải là trạng thái đích không.
Solution (giải pháp) là chuỗi các hành động hoặc trạng thái từ trạng thái ban đầu đến trạng thái đích, thỏa mãn yêu cầu của bài toán tìm kiếm.
![Informed Search Algorithms](InformedSearchAlgorithms.gif)
#### *Nhận xét:*
- Thuật toán A* là lựa chọn hàng đầu cho bài toán 8-puzzle nhờ khả năng tìm lời giải tối ưu với hiệu suất tốt khi sử dụng hàm heuristic phù hợp.
- Greedy Best-First Search nhanh nhưng không tối ưu, dễ mắc sai lầm trong không gian trạng thái phức tạp.
- IDA* là giải pháp thay thế cho A* khi bộ nhớ hạn chế, vẫn đảm bảo tính tối ưu nhưng đổi lại thời gian chạy có thể lâu hơn.
*Tóm lại,* Các thuật toán tìm kiếm có sử dụng thông tin (heuristic) giúp giảm đáng kể số trạng thái cần duyệt so với các thuật toán tìm kiếm không thông tin, đặc biệt trong các bài toán phức tạp như trò chơi 8-puzzle
#### *2.3. Local Search* 
Các thành phần chính của bài toán tìm kiếm
- Trạng thái ban đầu (Initial state): Điểm xuất phát của bài toán.
- Trạng thái đích (Goal state): Mục tiêu cần đạt được.
- Hành động (Actions): Các phép biến đổi để di chuyển giữa các trạng thái.
- Hàm chi phí (Cost function): Chi phí thực hiện hành động hoặc di chuyển.
- Hàm đánh giá (Heuristic function): Ước lượng mức độ gần trạng thái hiện tại đến trạng thái đích (đặc biệt trong tìm kiếm có thông tin).
Solution (Giải pháp): Chuỗi các hành động hoặc trạng thái từ trạng thái ban đầu đến trạng thái đích thỏa mãn yêu cầu bài toán.
![Local Search](LocalSearch.gif)
#### *Nhận xét:*
- Các thuật toán Hill Climbing đơn giản nhanh nhưng dễ bị kẹt tại cực trị địa phương, không đảm bảo tìm lời giải tối ưu trong 8-puzzle.
- Simulated Annealing cải thiện khả năng thoát khỏi cực trị địa phương, phù hợp với bài toán 8-puzzle phức tạp.
- Beam Search giúp cân bằng giữa bộ nhớ và thời gian, hiệu quả nếu chọn beam width phù hợp.
- Genetic Algorithm có thể tìm lời giải tốt trong không gian trạng thái lớn nhưng cần nhiều tính toán và tinh chỉnh tham số.

*Tóm lại,* Tìm kiếm cục bộ và tiến hóa cung cấp các phương pháp linh hoạt, có thể áp dụng trong 8-puzzle để tìm lời giải gần tối ưu nhanh hơn so với tìm kiếm toàn diện, nhưng không đảm bảo tối ưu tuyệt đối.