# Minimum Cost Assignment Algorithms
import time
import random


def generate_cost_matrix(n):
    """Generate an NxN cost matrix with random values between 20 and 200."""
    return [[random.randint(20, 200) for _ in range(n)] for _ in range(n)]


# Algorithm 1 : Hungarian Algorithm (Kuhn-Munkres) - Optimal O(n^3)
def hungarian_algorithm(cost_matrix):
    """
    Implements the Hungarian algorithm to find the minimum cost assignment.
    Returns (total_cost, assignment) where assignment[i] = j means
    employee i is assigned to task j.
    """
    n = len(cost_matrix)

    # Create working copy with padding row/col (1-indexed internally)
    u = [0] * (n + 1)  # potential for employees (rows)
    v = [0] * (n + 1)  # potential for tasks (cols)
    assignment = [0] * (n + 1)  # assignment[j] = employee assigned to task j

    for i in range(1, n + 1):
        # links[j] = employee that gives the shortest tentative connection to task j
        links = [0] * (n + 1)
        mins = [float('inf')] * (n + 1)  # min reduced cost to reach task j
        visited = [False] * (n + 1)

        assignment[0] = i  # virtual task 0 points to current employee
        j0 = 0  # start from virtual task

        while True:
            visited[j0] = True
            emp = assignment[j0]
            delta = float('inf')
            j1 = -1

            for j in range(1, n + 1):
                if visited[j]:
                    continue
                reduced = cost_matrix[emp - 1][j - 1] - u[emp] - v[j]
                if reduced < mins[j]:
                    mins[j] = reduced
                    links[j] = j0
                if mins[j] < delta:
                    delta = mins[j]
                    j1 = j

            # Update potentials
            for j in range(n + 1):
                if visited[j]:
                    u[assignment[j]] += delta
                    v[j] -= delta
                else:
                    mins[j] -= delta

            j0 = j1
            if assignment[j0] == 0:
                break

        # Augment along the path
        while j0 != 0:
            assignment[j0] = assignment[links[j0]]
            j0 = links[j0]

    # Build result: result[employee] = task (0-indexed)
    result = [0] * n
    total_cost = 0
    for j in range(1, n + 1):
        emp = assignment[j] - 1
        task = j - 1
        result[emp] = task
        total_cost += cost_matrix[emp][task]

    return total_cost, result


# Algorithm 2 : Greedy Algorithm - Heuristic O(n^2 log n)
def greedy_algorithm(cost_matrix):
    """
    Greedy approach: sort all (employee, task) pairs by cost ascending,
    then assign greedily ensuring each employee and task is used only once.
    Returns (total_cost, assignment) where assignment[i] = j means
    employee i is assigned to task j.
    """
    n = len(cost_matrix)

    # Build list of all (cost, employee, task) and sort by cost
    edges = []
    for i in range(n):
        for j in range(n):
            edges.append((cost_matrix[i][j], i, j))
    edges.sort()

    assigned_employees = set()
    assigned_tasks = set()
    result = [-1] * n
    total_cost = 0

    for cost, emp, task in edges:
        if emp in assigned_employees or task in assigned_tasks:
            continue
        result[emp] = task
        total_cost += cost
        assigned_employees.add(emp)
        assigned_tasks.add(task)
        if len(assigned_employees) == n:
            break

    return total_cost, result


def generate_choices(correct_answer):
    """Generate 3 answer choices: 1 correct + 2 wrong (within 5-15% of correct)."""
    pct_high = random.uniform(0.05, 0.15)
    pct_low = random.uniform(0.05, 0.15)
    wrong_high = round(correct_answer * (1 + pct_high))
    wrong_low = max(0, round(correct_answer * (1 - pct_low)))

    # Make sure all three values are different
    if wrong_high == correct_answer:
        wrong_high = correct_answer + random.randint(100, 500)
    if wrong_low == correct_answer:
        wrong_low = max(0, correct_answer - random.randint(100, 500))
    if wrong_high == wrong_low:
        wrong_high += random.randint(100, 500)

    choices = [correct_answer, wrong_high, wrong_low]
    random.shuffle(choices)
    return choices


def run_round(n):
    """Run a single game round: generate matrix, run both algorithms, return results with timing."""
    cost_matrix = generate_cost_matrix(n)

    # Run Hungarian
    start = time.perf_counter()
    h_cost, h_assignment = hungarian_algorithm(cost_matrix)
    h_time = (time.perf_counter() - start) * 1000  # ms

    # Run Greedy
    start = time.perf_counter()
    g_cost, g_assignment = greedy_algorithm(cost_matrix)
    g_time = (time.perf_counter() - start) * 1000  # ms

    return {
        "n": n,
        "cost_matrix": cost_matrix,
        "hungarian": {"cost": h_cost, "assignment": h_assignment, "time_ms": round(h_time, 4)},
        "greedy": {"cost": g_cost, "assignment": g_assignment, "time_ms": round(g_time, 4)},
    }
