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
