import random


# Define the graph structure with nodes and edges for Traffic Simulation
NODES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'T']

# Define edges as (from_node, to_node) tuples - Traffic Network
EDGES = [
    ('A', 'B'), ('A', 'C'), ('A', 'D'),
    ('B', 'E'), ('B', 'F'),
    ('C', 'E'), ('C', 'F'),
    ('D', 'F'),
    ('E', 'G'), ('E', 'H'),
    ('F', 'H'),
    ('G', 'T'),
    ('H', 'T')
]

# Fixed positions for drawing nodes on canvas - Updated layout
NODE_POSITIONS = {
    'A': (50, 250),     # Source - left
    'B': (180, 100),
    'C': (180, 250),
    'D': (180, 400),
    'E': (350, 150),
    'F': (350, 320),
    'G': (520, 150),
    'H': (520, 320),
    'T': (680, 250)     # Sink - right
}


def generate_capacities(min_cap=5, max_cap=15):
    """
    Generate random capacities for all edges in the graph.
    
    Args:
        min_cap: Minimum capacity (default: 5)
        max_cap: Maximum capacity (default: 15)
    
    Returns:
        Dictionary with edges as keys and capacities as values
        Example: {('A', 'B'): 10, ('A', 'C'): 7, ...}
    """
    capacities = {}
    for edge in EDGES:
        capacities[edge] = random.randint(min_cap, max_cap)
    
    return capacities


def get_graph_structure():
    """
    Get the graph structure (nodes and edges).
    
    Returns:
        Tuple of (nodes, edges)
    """
    return NODES, EDGES
