import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable, domain in self.domains.items():
            self.domains[variable] = {
                word for word in domain if len(word) == variable.length}

    def lets_value_for_y(self, x_value, y, x_index, y_index):
        """
        Receives a value for variable X, some other variable Y
        And the indices where they overlap

        Checks if the value X lets some possible value for Y such that
        the binary constraint that the characters at the overlap must 
        be equal is satisfied

        Returns True if such value in Y's domain exists, False otherwise
        """
        x_char = x_value[x_index]
        for y_value in self.domains[y]:
            y_char = y_value[y_index]
            if x_char == y_char:
                return True

        return False

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlap = self.crossword.overlaps[x, y]
        revised = False

        # check if x and y overlap
        if overlap is not None:
            x_index, y_index = overlap
            # make the domain a list so we can remove elements from it as we iterate over it
            for x_value in list(self.domains[x]):
                if not self.lets_value_for_y(x_value, y, x_index, y_index):
                    self.domains[x].remove(x_value)
                    revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = list(self.crossword.overlaps.keys())
        else:
            queue = arcs

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            try:
                assignment[var]
            except KeyError:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        values = set()
        for var, word in assignment.items():
            if var.length != len(word):
                return False

            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    x_index, y_index = self.crossword.overlaps[var, neighbor]
                    if word[x_index] != assignment[neighbor][y_index]:
                        return False

            values.add(word)

        # if the amount of values and the amount of variables differ, there must be repeated values
        if len(values) != len(assignment):
            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        def comparison_func(value, neighbors):
            """
            Checks how many neighbors's values does 'value' eliminate
            """
            # count of values crossed out
            n = 0
            for neighbor in neighbors:
                value_index, neighbor_index = self.crossword.overlaps[var, neighbor]
                # if overlap constraint isn't satisfied, the value would be crossed out
                for neighbor_val in self.domains[neighbor]:
                    if value[value_index] != neighbor_val[neighbor_index]:
                        n += 1

            return n

        # select all neighbors of variable which have not yet been assigned a value
        neighbors = [neighbor for neighbor in self.crossword.neighbors(var)
                     if neighbor not in assignment]

        return sorted(self.domains[var], key=lambda value: comparison_func(value, neighbors))

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # list of unassigned variables
        vars = [var for var in self.crossword.variables if var not in assignment]

        # sort them by the size of their domains
        smaller_domain_sorted_list = sorted(
            vars, key=lambda var: len(self.domains[var]))

        # flag to know if ALL vars are tied in domain size, or only some
        complete_tie = True

        smallest_domain_var = smaller_domain_sorted_list[0]

        # check if there's tie in domain size heuristic
        for i, var in enumerate(smaller_domain_sorted_list):
            # all of which have equal domain size as the smallest one are tied
            if len(self.domains[var]) == len(self.domains[smallest_domain_var]):
                continue

            # once we find one var with a domain size different from the smallest one,
            # we know which variables are tied (and we know that not all of them are)
            tied = smaller_domain_sorted_list[0:i]
            complete_tie = False
            break

        if complete_tie:
            tied = smaller_domain_sorted_list

        # select the one (or one of the ones) with the largest degree (degree given by the amount of neighbors)
        return sorted(tied, key=lambda var: len(self.crossword.neighbors(var)), reverse=True)[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.domains[var]:
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                else:
                    assignment.pop(var)
            else:
                assignment.pop(var)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
