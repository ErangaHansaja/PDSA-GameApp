from collections import defaultdict, deque
from time import perf_counter_ns


def ford_fulkerson(source, sink, capacities):
    """
    Calculate maximum flow using Ford-Fulkerson algorithm with DFS.
    
    Args:
        source: Source node (e.g., 'A')
        sink: Sink node (e.g., 'T')
        capacities: Dictionary of edge capacities {(from, to): capacity}
    
    Returns:
        Tuple of (max_flow_value, execution_time_seconds)
    """
    start_time_ns = perf_counter_ns()
    
    # Build residual graph
    residual = defaultdict(lambda: defaultdict(int))
    for (u, v), cap in capacities.items():
        residual[u][v] = cap
    
    # Get all nodes
    nodes = set()
    for u, v in capacities.keys():
        nodes.add(u)
        nodes.add(v)
    
    def dfs_path(s, t, visited):
        """Find augmenting path using DFS."""
        if s == t:
            return [t]
        
        visited.add(s)
        for neighbor in residual[s]:
            if neighbor not in visited and residual[s][neighbor] > 0:
                path = dfs_path(neighbor, t, visited)
                if path:
                    return [s] + path
        return None
    
    max_flow = 0
    
    while True:
        visited = set()
        path = dfs_path(source, sink, visited)
        
        if not path:
            break
        
        # Find minimum residual capacity along the path
        path_flow = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            path_flow = min(path_flow, residual[u][v])
        
        # Update residual capacities
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual[u][v] -= path_flow
            residual[v][u] += path_flow
        
        max_flow += path_flow
    
    execution_time = (perf_counter_ns() - start_time_ns) / 1_000_000_000
    return max_flow, execution_time


def edmonds_karp(source, sink, capacities):
    """
    Calculate maximum flow using Edmonds-Karp algorithm (BFS-based).
    
    Args:
        source: Source node (e.g., 'A')
        sink: Sink node (e.g., 'T')
        capacities: Dictionary of edge capacities {(from, to): capacity}
    
    Returns:
        Tuple of (max_flow_value, execution_time_seconds)
    """
    start_time_ns = perf_counter_ns()
    
    # Build residual graph
    residual = defaultdict(lambda: defaultdict(int))
    for (u, v), cap in capacities.items():
        residual[u][v] = cap
    
    def bfs_path(s, t, parent):
        """Find augmenting path using BFS."""
        visited = {s}
        queue = deque([s])
        
        while queue:
            u = queue.popleft()
            
            for v in residual[u]:
                if v not in visited and residual[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    
                    if v == t:
                        return True
                    
                    queue.append(v)
        
        return False
    
    max_flow = 0
    
    while True:
        parent = {}
        if not bfs_path(source, sink, parent):
            break
        
        # Find minimum residual capacity along the path
        path_flow = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual[u][v])
            v = u
        
        # Update residual capacities
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow
            residual[v][u] += path_flow
            v = u
        
        max_flow += path_flow
    
    execution_time = (perf_counter_ns() - start_time_ns) / 1_000_000_000
    return max_flow, execution_time
