from itertools import combinations

assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        box(string): a string identifying the key/box to be assigned ('A1', 'H9', etx.)
        value(string): the value to be assigned to the key ('123456789', '27', etc.)
    Returns:
        the values dictionary with the updated assignment
        As a side effect, updates the assigments list with a copy of values.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of possible twins - boxes with exactly two possible values.
    possible_twins = [box for box in values.keys() if len(values[box]) == 2]

    # For every pair of twins, if they have the same value and share a
    # unit, we found a naked twin. Let's make a list for further processing
    twins = [(box1, box2, unit1) for (box1, box2) in combinations(possible_twins, 2) \
                     for unit1 in units[box1] for unit2 in units[box2] \
                     if values[box1] == values[box2] and unit1 == unit2]

    # For each naked twin, go through the other boxes in the shared unit and
    # eliminate the values shared by the twin boxes.
    for (box1, box2, unit) in twins:
        for box in unit:
            if (box != box1 and box!= box2):
                for char in values[box1]:
                    values[box] = values[box].replace(char, '')

    return values

def cross(A, B):
    """Cross product of elements in A and elements in B.

    Args:
        A(string): A string representing rows in a table
        B(string): A strring representing columns in a table

    Returns:
        A list of all possible combinations resulting from
        taking an element from A followed by an element from B
    """
    return [s+t for s in A for t in B]


def grid_values(grid):
    """Convert grid into a dict of {square: char} with '123456789' for empties.

    Args:
        grid(string): a string representing a partially solved sudoku puzzle.
                      The string should be 81 characters with a '.' for any
                      unassigned item and a number valued 1 to 9 inclusive for
                      assigned items.
    Returns:
        a dictionary with box labels ('A1', 'H7', etc.) as keys and either the number
        assigned to the box or '123456789' for unassigned boxes as values.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    return dict(zip(boxes, chars))

def display(values):
    """Display these values as a 2-D grid.

    Args:
        values(dict): a dictionary with box labels as keys and a string of numbers as values.

    Returns:
        no return value. This function is for printing side-effects only
    """

    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    """For each solved/assigned value, eliminate it as a candidate for all peers

    Args:
        values(dict): a dictionary with box labels as keys and a string of numbers as values.

    Returns:
        the mutated values dictionary with assigned values eliminated from peers
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values


def only_choice(values):
    """For each unit, determine if there is only one box remaining as a choice for a
       given value. If so, assign the value to the box.

    Args:
        values(dict): a dictionary with box labels as keys and a string of numbers as values.

    Returns:
        the mutated values dictionary with 'only choice' values assigned to the appropriate box.
    """
    for unit in unitlist:
        for digit in '123456789':
            # Count the number of boxes containing a given digit
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    """Cycles through our constraints (eliminate, naked_twins, only_choice) for reducing puzzles.
    Iteratively reduces puzzle until progress (measured by an increase in solved boxes) stalls.

    Args:
        values(dict): a dictionary with box labels as keys and a string of numbers as values.

    Returns:
        the mutated values dictionary with assig
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Propagate constraints. Prefer to use only_choice last as it is the function
        # that assigns values to boxes while the others just eliminate values from boxes.
        values = eliminate(values)
        values = naked_twins(values)
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def solve(grid_string):
    """Solve a sudoku puzzle.

    Args:
        grid_string(string): a string representing a partially solved sudoku puzzle.
                      The string should be 81 characters with a '.' for any
                      unassigned item and a number valued 1 to 9 inclusive for
                      assigned items.

    Returns:
        a dictionary representing a solved sudoku puzzle.
    """
    values = grid_values(grid_string)
    return search(values)

def search(values):
    """Using depth-first search and propagation, create a search tree and solve the sudoku.

    Args:
        values(dict): a dictionary with box labels as keys and a string of numbers as values.

    Returns:
        a dictionary representing a solved sudoku puzzle

    """
    # First, reduce the puzzle
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Chose one of the unfilled square s with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

# Set up some useful global values representing features of a sudoku puzzle
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[s+t for (s,t) in zip(rows, cols)], [s+t for (s,t) in zip(rows[::-1], cols)]]
unitlist = row_units + column_units + square_units+diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
