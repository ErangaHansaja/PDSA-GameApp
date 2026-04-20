import time
import heapq
from collections import deque

def bfs_min_moves(board):
    start_time = time.perf_counter()
    queue = deque([(1, [])]) 
    visited = {1}

    while queue:
        cell, path = queue.popleft()
        if cell == board.total_cells:
            end_time = time.perf_counter()
            return len(path), path, (end_time - start_time)

        for dice in range(1, 7):
            next_cell = cell + dice
            if next_cell <= board.total_cells:
                temp = next_cell
                while temp in board.snakes or temp in board.ladders:
                    temp = board.snakes.get(temp) or board.ladders.get(temp)
                
                if temp not in visited:
                    visited.add(temp)
                    queue.append((temp, path + [dice]))
    return 0, [], 0
