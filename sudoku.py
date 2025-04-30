from collections import deque  # For efficient queue operations
import copy  # For deep copying domains during backtracking
import random

N = 9  # Standard Sudoku grid size (9x9)

def get_box(i, j):
    """Returns top-left coordinates of the 3x3 box containing cell (i,j)"""
    return (i // 3) * 3, (j // 3) * 3

def generate_neighbors():
    """
    Generates a dictionary mapping each cell to its constrained neighbors
    (cells in same row, column, or 3x3 box)
    """
    neighbors = {}
    for i in range(N):
        for j in range(N):         
            cell = (i, j)
            n = set()
            # Add all cells in same row
            for k in range(N):
                if k != j:
                    n.add((i, k))
                # Add all cells in same column
                if k != i:
                    n.add((k, j))
            # Add all cells in same 3x3 box
            bi, bj = get_box(i, j)
            for r in range(bi, bi + 3):
                for c in range(bj, bj + 3):
                    if (r, c) != (i, j):
                        n.add((r, c))
            neighbors[cell] = n
    return neighbors

def ac3(domains, neighbors):
    """
    AC-3 algorithm for constraint propagation
    Returns False if inconsistency found, True otherwise
    """
    # Initialize queue with all constraint pairs
    queue = deque([(xi, xj) for xi in neighbors for xj in neighbors[xi]])
    
    while queue:
        xi, xj = queue.popleft()
        # Revise domains and check if changes occurred
        if revise(domains, xi, xj):
            if not domains[xi]:  # Domain became empty
                return False
            # Add new constraints to queue
            for xk in neighbors[xi] :#- {xj}:
                queue.append((xk, xi))
    return True

def revise(domains, xi, xj):
    """
    Makes xi arc-consistent with xj
    Removes values from xi's domain that have no support in xj's domain
    Returns True if domain was revised, False otherwise
    """
    revised = False
    to_remove = []
    # Check each value in xi's domain
    for x in domains[xi]:
        # If no value in xj's domain satisfies x != y
        if not any(x != y for y in domains[xj]):
            to_remove.append(x)
            revised = True
    # Remove inconsistent values
    for val in to_remove:
        domains[xi].remove(val)
    return revised

def backtrack(domains, neighbors):
    """
    Backtracking search with Minimum Remaining Values (MRV) heuristic
    Returns solution domains if found, None otherwise
    """
    # Base case: all variables have single values
    if all(len(domains[cell]) == 1 for cell in domains):
        return domains
    
    # Select unassigned variable with fewest remaining values (MRV)
    unassigned = [cell for cell in domains if len(domains[cell]) > 1]
    var = min(unassigned, key=lambda cell: len(domains[cell]))
    
    # Try each value in the domain
    for value in domains[var]:
        new_domains = copy.deepcopy(domains)
        new_domains[var] = {value}  # Assign value
        
        # Maintain arc consistency
        if ac3(new_domains, neighbors):
            result = backtrack(new_domains, neighbors)  # Recursive call
            if result:
                return result
    return None  # No solution found

def grid_to_domains(grid):
    """Converts Sudoku grid to CSP domains dictionary"""
    domains = {}
    for i in range(N):
        for j in range(N):
            if grid[i][j] == 0:  # Empty cell
                domains[(i, j)] = set(range(1, 10))  # Possible values 1-9
            else:  # Pre-filled cell
                domains[(i, j)] = {grid[i][j]}  # Fixed value
    return domains

def domains_to_grid(domains):
    """Converts solved domains back to Sudoku grid format"""
    return [[list(domains[(i, j)])[0] for j in range(N)] for i in range(N)]

def print_grid(grid):
    """Prints Sudoku grid with borders between 3x3 boxes"""
    for i, row in enumerate(grid):
        print(" ".join(str(num) if num != 0 else '.' for num in row))
        if (i + 1) % 3 == 0 and i != 8:  # Add horizontal line after every 3 rows
            print("-" * 21)

def get_user_input():
    """Gets Sudoku puzzle input from user"""
    grid = [[0]*9 for _ in range(9)]
    for _ in range(20):  # fill 20 random cells
        i, j = random.randint(0, 8), random.randint(0, 8)
        if grid[i][j] == 0:
            nums = list(range(1, 10))
            random.shuffle(nums)
            for val in nums:
                grid[i][j] = val
                domains = grid_to_domains(grid)
                if ac3(domains, generate_neighbors()):
                    break
                grid[i][j] = 0
    return grid

# Main execution
if __name__ == "__main__":
    # Get puzzle from user
    puzzle = get_user_input()
    print("\nInitial Puzzle:")
    print_grid(puzzle)

    # Generate neighbors and convert to CSP representation
    neighbors = generate_neighbors()
    domains = grid_to_domains(puzzle)

    # Solve using AC-3 and backtracking
    if ac3(domains, neighbors):
        result = backtrack(domains, neighbors)
        if result:
            print("\nSolved Puzzle:")
            solved = domains_to_grid(result)
            print_grid(solved)
        else:
            print("\nNo solution found.")
    else:
        print("\nAC-3 failed to establish consistency.")
        