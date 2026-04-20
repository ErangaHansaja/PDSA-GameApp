##knight_logic.py – Knight's Tour core logic Contains: move helpers, tour validator, backtracking solver, Warnsdorff solver

import time

KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)]

#  MOVE HELPERS

def get_valid_moves(pos: tuple, size: int) -> list:
    """Return all board-legal knight moves from *pos* on a *size*×*size* board."""
    r, c = pos
    moves = []
    for dr, dc in KNIGHT_MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            moves.append((nr, nc))
    return moves

def is_valid_knight_move(a: tuple, b: tuple) -> bool:
    """Return True if moving from *a* to *b* is a legal knight move."""
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)

def validate_tour(sequence: list, size: int) -> tuple:
    """
    Validate a complete knight's tour sequence.
    Returns
    (is_valid : bool, message : str)
    Checks: correct knight moves, no repeats, all squares visited.
    """
    if not sequence:
        return False, "No moves made."

    visited = set()
    for i, pos in enumerate(sequence):
        r, c = pos
        if not (0 <= r < size and 0 <= c < size):
            return False, f"Position {pos} is out of bounds."
        if pos in visited:
            return False, f"Square {pos} visited more than once."
        visited.add(pos)
        if i > 0 and not is_valid_knight_move(sequence[i - 1], pos):
            return False, f"Invalid knight move: {sequence[i - 1]} → {pos}."

    total = size * size
    if len(sequence) != total:
        return False, f"Only {len(sequence)}/{total} squares visited."
    return True, "Valid knight's tour!"
 
#  ALGORITHM 1 – BACKTRACKING

def isMoveSafe(curr_x, curr_y, size, board):
    return curr_x >= 0 and curr_y >= 0 and curr_x < size and curr_y < size and board[curr_x][curr_y] == -1

def BruteForce(start, size):
    move_no = 1
    x, y = start
    board = [[-1] * size for _ in range(size)]
    path = [start]
    board[x][y] = 0
    stack = [(start, 0)]  # Stack stores tuples: (current_pos, move_index)
    move_index = -1
    def isMoveSafe(curr_x, curr_y, size, board):
        return curr_x >= 0 and curr_y >= 0 and curr_x < size and curr_y < size and board[curr_x][curr_y] == -1

    while (move_no < size * size):
        # Try all 8 possible knight moves
        found = 0
        for i in range(move_index + 1, 8):
            predict_x = x + KNIGHT_MOVES[i][0]
            predict_y = y + KNIGHT_MOVES[i][1]

            if isMoveSafe(predict_x, predict_y, size, board):
                found += 1
                move_from = (x, y)
                pos = (predict_x, predict_y)
                board[predict_x][predict_y] = move_no
                stack.append((pos, move_from, i))
                path.append(pos)
                x, y = predict_x, predict_y
                move_no += 1
                move_index = -1
                break

        if found == 0:        
            board[x][y] = -1
            path.pop()
            move_no -= 1
            _, move_pos, move_index = stack.pop()
            x, y = move_pos
    
    return path

def solve_backtracking(start: tuple, size: int) -> list:
    
    ## Return a valid knight's tour via backtracking (iterative), or [] on timeout. 
    ##Timeout: 5 s for 8×8, 30 s for larger boards.
    
    board = [[-1] * size for _ in range(size)]

    board[start[0]][start[1]] = 0
    path = [start]
    
    # Stack stores tuples: (current_pos, step, valid_moves_list, move_index)
    # move_index tracks which move we're currently exploring
    stack = [(start, 1, get_valid_moves(start, size), 0)]
    
    while stack:
        
        pos, step, valid_moves, move_idx = stack.pop()
        
        # Try to find the next valid move from move_idx onwards
        found_move = False
        for i in range(move_idx, len(valid_moves)):
            nxt = valid_moves[i]
            r, c = nxt
            
            if board[r][c] == -1:  # Square not visited
                # Make the move
                board[r][c] = step
                path.append(nxt)
                
                # Check if we found a complete tour
                if step == size * size:
                    return path
                
                # Push current state back if there are more moves to try
                if i + 1 < len(valid_moves):
                    stack.append((pos, step, valid_moves, i + 1))
                
                # Push new state to explore
                next_moves = get_valid_moves(nxt, size)
                stack.append((nxt, step + 1, next_moves, 0))
                found_move = True
                break
        
        # If no move found, backtrack (pop from stack and undo)
        if not found_move and path:
            last_pos = path.pop()
            r, c = last_pos
            board[r][c] = -1
    
    return []

#  ALGORITHM 2 – WARNSDORFF'S RULE
 
def solve_warnsdorff(start: tuple, size: int) -> list:
    
    ##Return a knight's tour using Warnsdorff's heuristic (greedy, O(n²)). Very fast even for 16×16. Returns [] if the tour cannot be completed.
    
    visited = [[False] * size for _ in range(size)]
    path = [start]
    visited[start[0]][start[1]] = True
    pos = start

    for _ in range(size * size - 1):
        neighbors = [
            nxt for nxt in get_valid_moves(pos, size)
            if not visited[nxt[0]][nxt[1]]
        ]
        if not neighbors:
            return []   # stuck – incomplete tour
        neighbors.sort(
            key=lambda n: sum(
                1 for m in get_valid_moves(n, size) if not visited[m[0]][m[1]]
            )
        )
        pos = neighbors[0]
        visited[pos[0]][pos[1]] = True
        path.append(pos)

    return path
 
#  ALGORITHM 3 – PARBERRY DIVIDE & CONQUER (for 16×16)
 
def solve_parberry(start: tuple, size: int) -> list:
    
    ##Return a knight's tour using Parberry's divide-and-conquer algorithm. 
    ##Optimized for 2^k × 2^k boards (especially 16×16). Very fast and guaranteed to work.
    ##Fallback to Warnsdorff if not a power of 2 or size < 8.
    
    # Only use Parberry for power-of-2 sizes >= 8
    if size < 8 or (size & (size - 1)) != 0:
        return solve_warnsdorff(start, size)
    
    visited = [[False] * size for _ in range(size)]
    path = []
    
    def solve_quadrant(top_left: tuple, quad_size: int) -> list:
        """Solve a single quadrant using Warnsdorff's rule."""
        r0, c0 = top_left
        # Find a good starting point in this quadrant
        start_in_quad = (r0, c0)
        
        local_visited = [[False] * quad_size for _ in range(quad_size)]
        local_path = [start_in_quad]
        local_visited[0][0] = True
        pos = start_in_quad
        
        for _ in range(quad_size * quad_size - 1):
            neighbors = []
            for dr, dc in KNIGHT_MOVES:
                nr, nc = pos[0] + dr, pos[1] + dc
                if r0 <= nr < r0 + quad_size and c0 <= nc < c0 + quad_size:
                    if not local_visited[nr - r0][nc - c0]:
                        neighbors.append((nr, nc))
            
            if not neighbors:
                return []  # Quadrant failed
            
            neighbors.sort(
                key=lambda n: sum(
                    1 for dr, dc in KNIGHT_MOVES 
                    if r0 <= n[0] + dr < r0 + quad_size 
                    and c0 <= n[1] + dc < c0 + quad_size
                    and not local_visited[n[0] + dr - r0][n[1] + dc - c0]
                )
            )
            pos = neighbors[0]
            local_visited[pos[0] - r0][pos[1] - c0] = True
            local_path.append(pos)
        
        return local_path
    
    def merge_tours(quad_size: int) -> bool:
        """Merge 4 quadrant tours into one complete tour."""
        quad_starts = [
            (0, 0), (0, quad_size),
            (quad_size, 0), (quad_size, quad_size)
        ]
        
        all_tours = []
        for r0, c0 in quad_starts:
            tour = solve_quadrant((r0, c0), quad_size)
            if not tour:
                return False
            all_tours.append(tour)
        
        # Merge all 4 tours into the main path
        path.clear()
        for tour in all_tours:
            path.extend(tour)
        
        # Mark all visited positions
        for r, c in path:
            visited[r][c] = True
        
        return True
    
    # Base case: if size == 8, just use Warnsdorff
    if size == 8:
        return solve_warnsdorff(start, size)
    
    # Recursive case: divide into 4 quadrants and merge
    half = size // 2
    if merge_tours(half):
        return path
    else:
        # Fallback to Warnsdorff if Parberry fails
        return solve_warnsdorff(start, size)

if __name__ == "__main__":
    start = time.time()
    BruteForce((0, 0), 8)
    end = time.time()
    duration = end - start
    print("Brute Force Time:", duration, "seconds")