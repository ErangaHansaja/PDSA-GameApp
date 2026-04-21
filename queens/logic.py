import time
import threading


class NQueensLogic:
    def __init__(self, size=16, max_solutions=30):
        self.size = size
        self.max_solutions = max_solutions

    def is_valid(self, queens):
        for i in range(len(queens)):
            for j in range(i + 1, len(queens)):
                r1, c1 = queens[i]
                r2, c2 = queens[j]
                if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                    return False
        return True

    def backtrack_solver(self, row, current, results, solutions):
        if results[0] >= self.max_solutions:
            return

        if row == self.size:
            results[0] += 1
            solutions.append(current.copy())
            return

        for col in range(self.size):
            temp = current + [(row, col)]
            if self.is_valid(temp):
                self.backtrack_solver(row + 1, temp, results, solutions)

    def run_sequential(self):
        results = [0]
        solutions = []
        start = time.time()

        self.backtrack_solver(0, [], results, solutions)

        return results[0], time.time() - start, solutions

    def run_threaded(self):
        total = [0]
        solutions = []
        lock = threading.Lock()
        threads = []
        start = time.time()

        def task(start_col):
            local_solutions = []

            def limited_backtrack(row, current):
                # STOP if global limit reached
                with lock:
                    if total[0] >= self.max_solutions:
                        return

                if row == self.size:
                    with lock:
                        if total[0] < self.max_solutions:
                            total[0] += 1
                            solutions.append(current.copy())
                    return

                for col in range(self.size):
                    temp = current + [(row, col)]

                    if self.is_valid(temp):
                        limited_backtrack(row + 1, temp)

            limited_backtrack(1, [(0, start_col)])

        # Create threads
        for c in range(self.size):
            t = threading.Thread(target=task, args=(c,))
            threads.append(t)
            t.start()

        # Wait for all
        for t in threads:
            t.join()

        return total[0], time.time() - start, solutions
