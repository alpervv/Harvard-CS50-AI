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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        for var in self.crossword.variables:
            domain_to_iterate = list(self.domains[var])
            for value in domain_to_iterate:
                # if possible value's legth is not consistent remove it
                if len(value) != var.length:
                    self.domains[var].remove(value)
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Ignore the constraint that all words must be unique

        is_revision_made = False
        # check if x and y overlap. If they do check consistency.
        if self.crossword.overlaps[x, y] != None:
            x_position, y_position = self.crossword.overlaps[x, y]
            domain_to_iterate = list(self.domains[x])
            for x_value in domain_to_iterate:
                # initially assume x_value is not consistent with y, change if there is y suitable y value
                value_consistent = False
                for y_value in self.domains[y]:
                    if y_value[y_position] == x_value[x_position]:
                        value_consistent = True
                        break
                # remove the value from x's domain if not consistent with y
                if not value_consistent:
                    self.domains[x].remove(x_value)
                    is_revision_made = True # Made change in domain of x

        return is_revision_made
    

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            queue = []
            var_list = list(self.domains.keys())
            # find all arcs
            for i in range(len(self.domains)):
                for j in range(len(self.domains)):
                    if i != j:
                        queue.append((var_list[i], var_list[j]))
        else:
            queue = arcs
        
        for arc in queue:
            x = arc[0]
            y = arc[1]
            # Force arc consistency. If there is change append arcs to queue. If no change is made do nothing.
            if self.revise(x, y) == True:
                neighbors = self.crossword.neighbors(x) # set of neighbors of x
                for neighbor in neighbors:
                    queue.append((neighbor, x)) # append a tuple (neighbor, x) to queue

                # check if there are any words left in the domain of x
                if len(self.domains[x]) == 0:
                    return False
        
        # Updated all the arcs and all domains are non-empty
        return True
       

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        is_all_assigned = True
        for var in self.crossword.variables:
            # check if var is a key in dictionary first
            if var in assignment.keys():
                # check if var is assigned to a word
                if assignment[var] not in self.crossword.words:
                    is_all_assigned = False
                    break
            else:
                is_all_assigned = False
                break
        
        return is_all_assigned


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        list_of_values = list(assignment.values())

        # check if any value repeats. If it does assignment is inconsistent
        for val in list_of_values:
            if list_of_values.count(val) > 1:
                return False
            
        # check if all words fit (length). If one doesn't assignment is inconsistent
        for var in assignment.keys():
            if len(assignment[var]) != var.length:
                return False
            
        # check if all overlaps are consistent
        for v1, v2 in self.crossword.overlaps.keys():
            # If no overlap there will be an error when unpacking
            
            if self.crossword.overlaps[v1, v2] != None:
                v1_position, v2_position = self.crossword.overlaps[v1, v2]
                # Sınce all variables don't have to be assigned check if they are in assignment
                if v1 in assignment.keys() and v2 in assignment.keys():
                    # check if overlap is conflicting or not
                    if assignment[v1][v1_position] != assignment[v2][v2_position]:
                        return False
        
        return True
        
    

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        rule_out_dict = dict() # maps domain values to number of options they rule out
        for word in self.domains[var]:
            rule_out_num = 0
            for neighbor in self.crossword.neighbors(var):
                pos1, pos2 = self.crossword.overlaps[var, neighbor]
                for neighbor_word in self.domains[neighbor]:
                    if word[pos1] != neighbor_word[pos2]:
                        rule_out_num += 1
            rule_out_dict[word] = rule_out_num
          
        return sorted(rule_out_dict, key=lambda k: rule_out_dict[k])
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        current_domain_size = max([len(domain) for domain in self.domains.values()]) # Initially set to a large number
        current_neighbor_count = max([len(self.crossword.neighbors(var)) for var in self.crossword.variables])  # Initially set to a large number
        
        for var in self.crossword.variables:
            # check if var is not assigned and its domain is smaller than current smallest domain.
            if var not in assignment.keys() and len(self.domains[var]) < current_domain_size:
                var_to_return = var
                current_domain_size = len(self.domains[var])
                current_neighbor_count = len(self.crossword.neighbors(var))
            
            # If domains are of equal size check neighbor count
            if var not in assignment.keys() and len(self.domains[var]) == current_domain_size:
                if len(self.crossword.neighbors(var)) <= current_neighbor_count:
                    var_to_return = var
                    current_domain_size = len(self.domains[var])
                    current_neighbor_count = len(self.crossword.neighbors(var))

        return var_to_return
    

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

        if len(self.domains[var]) == 0:
            return None

        var_domain = self.order_domain_values(var, assignment)
        
        for var_value in var_domain:
            assignment[var] = var_value
            # check if new assignment is consistent
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result != None:
                    return result
        
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
