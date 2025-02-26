import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """
    
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.mines = set()
        self.safes = set()
    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"
    


    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.mines.union(self.cells)
        return self.mines
        

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.safes.union(self.cells)
        return self.safes
        

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        #mark the cell mine
        if cell in self.cells:
            self.mines.add(cell)
            #remove the cell as it is marked as mine
            self.cells.discard(cell)
            self.count -=1
            

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        #mark the cell safe
        if cell in self.cells:
            self.safes.add(cell)
            #Remove the cell as it is marked safe
            self.cells.discard(cell)
           

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []
        
    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        

        #find a list of neighbouring cells
        i, j = cell
        neighbour_cells=[]
        for a in range(max(0, i-1), min(i+2, self.height)):
            for b in range(max(0, j-1), min(j+2, self.width)):
                neighbour_cells.append((a, b))
        neighbour_cells.remove(cell) #remove original cell
        
        #create a new sentence, only with cells whose state is undetermined
        neighbour_cells_for_iteration = neighbour_cells.copy()
        for neighbour_cell in neighbour_cells_for_iteration:
            if neighbour_cell in self.safes:
                neighbour_cells.remove(neighbour_cell)
            elif neighbour_cell in self.mines:
                neighbour_cells.remove(neighbour_cell)
                count-=1 #Reduce count by 1 as a mine is removed from sentence
        
        new_sentence = Sentence(neighbour_cells, count)
        self.knowledge.append(new_sentence)
        
        previous_knwoledge = None
        new_knwoledge = self.knowledge.copy()
        
        #Modify knowledge untill no modifications can be made
        while new_knwoledge != previous_knwoledge:

            for i in range(3):
                #Check if sentences exist with all mines marked
                knowledge_to_iterate_over = self.knowledge.copy() #make a copy of knowledge so it doesn't change in size during iteration
                for sentence in knowledge_to_iterate_over:
                    if sentence.count == 0:
                        cells_to_iterate_over = list(sentence.cells) #create a new object so set doesn't change size during iteration
                        for safe_cell in cells_to_iterate_over:
                            self.mark_safe(safe_cell)
                        self.knowledge.remove(sentence)
                
                #Check if sentences exist with all safes marked
                knowledge_to_iterate_over = self.knowledge.copy() #make a copy of knowledge so it doesn't change in size during iteration
                for sentence in knowledge_to_iterate_over:
                    if len(sentence.cells) == sentence.count:
                        cells_to_iterate_over = list(sentence.cells) #create a new object so set doesn't change size during iteration
                        for cell_with_mine in cells_to_iterate_over:
                            self.mark_mine(cell_with_mine)
                        self.knowledge.remove(sentence)

            #make new sentences
            cartesian_product = [(sentence1, sentence2) for sentence1 in self.knowledge for sentence2 in self.knowledge]
            for sentence1, sentence2 in cartesian_product:
                if sentence1 != sentence2:
                    if sentence1.cells.issubset(sentence2.cells):
                        new_sentence = Sentence(sentence2.cells.difference(sentence1.cells), sentence2.count-sentence1.count)
                        if new_sentence not in self.knowledge:
                            self.knowledge.append(new_sentence)
                    if sentence2.cells.issubset(sentence1.cells):
                        new_sentence = Sentence(sentence1.cells.difference(sentence2.cells), sentence1.count-sentence2.count)
                        if new_sentence not in self.knowledge:
                            self.knowledge.append(new_sentence)
            
            previous_knwoledge = new_knwoledge
            new_knwoledge = self.knowledge.copy()
    
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                self.moves_made.add(cell)
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        list_of_unknown_cells = []
        #Find all cells which are not in moves_made and are not mines
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i ,j) not in self.mines:
                    list_of_unknown_cells.append((i, j))
        #check if there is a cell available
        if list_of_unknown_cells != []:
            random_index = random.randint(0, len(list_of_unknown_cells)-1)
            return list_of_unknown_cells[random_index]
        return None
        
