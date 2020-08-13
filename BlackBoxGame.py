# Author: Christina Wilson
# Date: 8/13/2020
# Description: This program allows users to play a board game called Black Box. The first user sets up the board by
#              entering the positions of atoms. The second user tries to find the atoms by directly guessing the atoms
#              position or by entering the entry point of a ray that can hit an atom in its path, detour from an atom it
#              almost hits, or miss an atom. The second user starts with 25 points. Each entry and exit location deducts
#              a point and each incorrect atom position guess deducts 5 points.


class BlackBoxGame:
    """
    Represents the Black Box Game.
    Responsibilities: Sets up the board with at least one atom. Allows the user to shoot a ray through the board and
    guess an atom location. Keeps track of score and number of atoms not guessed yet. Prints out the board whenever a
    move is made. Keep track of entry points, exit points, and atom guesses. Keeps track of score. Informs player
    when they win or lose.
    Collaborators: Ray, Atom
    """

    def __init__(self, list_atoms):
        """
        Initializes a Black Box Game. The user enters a list of tuples representing atom positions. Sets the player's
        score to 25. Sets up Rays and Atom classes.
        """

        # Player starts with 25 points
        self._score = 25

        # Create Rays class
        self._my_rays = Rays(list_atoms)

        # Creates atoms with Atom class
        self._my_atoms = Atom(list_atoms)

    def shoot_ray(self, row, column):
        """
        Allows the user to enter a the position (row and column) of where the ray enters. Returns a tuple of the row
        and column of the exit border square. Returns False if user enters a corner square or non-border square.
        Returns None if there is no exit border square.
        """

        # Check for corner squares
        if (row == 0 or row == 9) and (column == 0 or column == 9):
            return False

        # Check for non-border squares
        if row != 0 and row != 9 and column != 0 and column != 9:
            return False

        # Deduct point if first time using this entry position
        if (row, column) not in self._my_rays.get_entry_exit_positions():
            self._my_rays.add_entry_exit_position(row, column)
            self.deduct_score(1)

        # Shoot the ray in the correct direction
        result = None
        if row == 0:
            result = self._my_rays.ray_movement(row, column, 'DOWN')
        if row == 9:
            result = self._my_rays.ray_movement(row, column, 'UP')
        if column == 0:
            result = self._my_rays.ray_movement(row, column, 'RIGHT')
        if column == 9:
            result = self._my_rays.ray_movement(row, column, 'LEFT')
        if result is not None:
            if result not in self._my_rays.get_entry_exit_positions():
                self._my_rays.add_entry_exit_position(result[0], result[1])
                self.deduct_score(1)
        return result

    def guess_atom(self, row, column):
        """
        Allows the user to enter the position (row and column) of where they think an atom is located. Returns True
        if there is an atom there and False if not. Also checks if player wins or loses and returns statements
        appropriate for each condition.
        """

        # If guess correctly, remove atom from atom list and when there are no atoms left, player wins
        for atom in self._my_atoms.get_atoms():
            if atom == (row, column):
                self._my_atoms.remove_atom(row, column)
                if self.atoms_left() == 0:
                    return 'Congratulations! You have won the game!'
                return True

        # If guess incorrectly, add guess to guess list and deduct score (no deduction for repeat guesses)
        else:
            if (row, column) in self._my_atoms.get_atom_guesses():
                return False
            else:
                self._my_atoms.add_to_atom_guesses(row, column)
                self.deduct_score(5)
                return False

    def atoms_left(self):
        """Returns the number of atoms that haven't been guessed yet."""
        count = 0
        for item in self._my_atoms.get_atoms():
            count += 1
        return count

    def deduct_score(self, deduction):
        """Deducts the score. The score is 25 at the beginning of the game."""
        self._score -= deduction
        if self.get_score() == 0:
            return 'Sorry, you have lost the game.'

    def get_score(self):
        """Returns the current score."""
        return self._score


class Rays:
    """
    Represents all possible rays and the effects they can have.
    Responsibilities: Determines if there will be a hit, detour, or reflection. Keeps track of entry and exit positions.
    Collaborator: BlackBoxGame
    """

    def __init__(self, atoms):
        """
        Initializes rays. Takes a list of atom tuples as a parameter because the movement of rays depends on location
        of atoms. Creates lists accumulating th entry and exit position of rays. Initializes row, column and direction
        and set to None so these can be used to describe future rays.
        """
        self._ray_atoms = atoms
        self._entry_exit_positions = []

        # The following are used to follow a single ray
        self._row = None
        self._column = None
        self._direction = None

    def get_entry_exit_positions(self):
        """Returns list of ray entry positions (tuples)."""
        return self._entry_exit_positions

    def add_entry_exit_position(self, row, column):
        """Adds a ray entry position (tuple)."""
        self._entry_exit_positions.append((row, column))

    def ray_movement(self,row,column,direction):
        """
        Figures out where ray will move. The row and column parameters make up the starting entry position. Direction
        can be UP, DOWN, LEFT, or RIGHT.
        """

        # Set up ray
        if self._row == None:
            self._row = row
        if self._column == None:
            self._column = column
        if self._direction == None:
            self._direction = direction

        # Check for hit
        if self.hit(row, column, direction) == True:
            return None

        # Check for reflection
        if self.reflection(row, column) == True:
            return (row, column)

        # Check for deflection (this will also return exit point for miss)
        if direction == 'UP':
            return self.deflection_while_moving_up(row, column)
        if direction == 'DOWN':
            return self.deflection_while_moving_down(row, column)
        if direction == 'LEFT':
            return self.deflection_while_moving_left(row, column)
        if direction == 'RIGHT':
            return self.deflection_while_moving_right(row, column)

    def hit(self, row, column, direction):
        """Returns if the ray entering from (row,column) will hit an atom when heading in a certain direction."""

        if direction == 'UP':
            for atom in self._ray_atoms:
                if atom[1] == column and atom[0] < row:
                    return True

        if direction == 'DOWN':
            for atom in self._ray_atoms:
                if atom[1] == column and atom[0] > row:
                    return True

        if direction == 'LEFT':
            for atom in self._ray_atoms:
                if atom[0] == row and atom[1] < column:
                    return True

        if direction == 'RIGHT':
            for atom in self._ray_atoms:
                if atom[0] == row and atom[1] > column:
                    return True

    def reflection(self, row, column):
        """Returns if the ray will reflect."""

        if row == 9:
            for atom in self._ray_atoms:
                if atom[0] == 8:
                    if (atom[1] == column + 1) or (atom[1] == column - 1):
                        return True

        if row == 0:
            for atom in self._ray_atoms:
                if atom[0] == 1:
                    if (atom[1] == column + 1) or (atom[1] == column - 1):
                        return True

        if column == 9:
            for atom in self._ray_atoms:
                if atom[1] == 8:
                    if (atom[0] == row + 1) or (atom[0] == row - 1):
                        return True

        if column == 0:
            for atom in self._ray_atoms:
                if atom[1] == 1:
                    if (atom[0] == row + 1) or (atom[0] == row - 1):
                        return True

    def deflection_while_moving_up(self, row, column):
        """
        Determines if a deflection will occur while ray is moving up. If there is no deflection, return the result of
        self.find_exit_position, which returns the exit position. If there is a deflection, determine the position of
        the ray after the deflection and return the result of self.ray_movement with the new row, column, and direction.
        """

        direction_after_detour = 'empty'
        deflection_atom = None

        for atom in self._ray_atoms:
            if (atom[1] == column + 1) and (atom[0] < row):
                if deflection_atom == None:
                    deflection_atom = atom
                elif atom[0] > deflection_atom[0]:
                    deflection_atom = atom
                direction_after_detour = 'LEFT'
            elif (atom[1] == column - 1) and (atom[0] < row):
                if deflection_atom == None:
                    deflection_atom = atom
                elif atom[0] > deflection_atom[0]:
                    deflection_atom = atom
                direction_after_detour = 'RIGHT'
        if deflection_atom == None:
            return self.find_exit_position(row,column,'UP')
        else:
            row = deflection_atom[0] + 1
            direction = direction_after_detour
            return self.ray_movement(row, column, direction)

    def deflection_while_moving_down(self, row, column):
        """
        Determines if a deflection will occur while ray is moving down. If there is no deflection, return the result of
        self.find_exit_position, which returns the exit position. If there is a deflection, determine the position of
        the ray after the deflection and return the result of self.ray_movement with the new row, column, and direction.
        """

        direction_after_detour = 'empty'
        deflection_atom = None

        for atom in self._ray_atoms:
            if (atom[1] == column + 1) and (atom[0] > row):
                if deflection_atom == None:
                    deflection_atom = atom
                elif atom[0] < deflection_atom[0]:
                    deflection_atom = atom
                direction_after_detour = 'LEFT'
            elif (atom[1] == column - 1) and (atom[0] > row):
                if deflection_atom == None:
                    deflection_atom = atom
                elif atom[0] < deflection_atom[0]:
                    deflection_atom = atom
                direction_after_detour = 'RIGHT'
        if deflection_atom == None:
            return self.find_exit_position(row,column,'DOWN')
        else:
            row = deflection_atom[0] - 1
            direction = direction_after_detour
            return self.ray_movement(row, column, direction)

    def deflection_while_moving_left(self, row, column):
        """
        Determines if a deflection will occur while ray is moving left. If there is no deflection, return the result of
        self.find_exit_position, which returns the exit position. If there is a deflection, determine the position of
        the ray after the deflection and return the result of self.ray_movement with the new row, column, and direction.
        """

        direction_after_detour = 'empty'
        deflection_atom = None

        for atom in self._ray_atoms:
            if (atom[0] == row + 1) and (atom[1] < column):
                if deflection_atom == None:
                    deflection_atom = atom
                elif atom[1] > deflection_atom[1]:
                    deflection_atom = atom
                direction_after_detour = 'UP'
            elif (atom[0] == row - 1) and (atom[1] < column):
                if deflection_atom == None:
                    deflection_atom = atom
                elif atom[1] > deflection_atom[1]:
                    deflection_atom = atom
                direction_after_detour = 'DOWN'
        if deflection_atom == None:
            return self.find_exit_position(row,column,'LEFT')
        else:
            column = deflection_atom[1] + 1
            direction = direction_after_detour
            return self.ray_movement(row, column, direction)

    def deflection_while_moving_right(self, row, column):
        """
        Determines if a deflection will occur while ray is moving right. If there is no deflection, return the result of
        self.find_exit_position, which returns the exit position. If there is a deflection, determine the position of
        the ray after the deflection and return the result of self.ray_movement with the new row, column, and direction.
        """

        direction_after_detour = 'empty'
        deflection_atom = None

        for atom in self._ray_atoms:
            if (atom[0] == row + 1) and (atom[1] > column):
                if deflection_atom == None:
                    deflection_atom = atom
                elif atom[1] < deflection_atom[1]:
                    deflection_atom = atom
                direction_after_detour = 'UP'
            elif (atom[0] == row - 1) and (atom[1] > column):
                if deflection_atom == None:
                    deflection_atom = atom
                elif atom[1] < deflection_atom[1]:
                    deflection_atom = atom
                direction_after_detour = 'DOWN'
        if deflection_atom == None:
            return self.find_exit_position(row,column,'RIGHT')
        else:
            column = deflection_atom[1] - 1
            direction = direction_after_detour
            return self.ray_movement(row, column, direction)

    def find_exit_position(self, row, column, direction):
        """
        Calculates and returns the exit position based on the current row, column, and direction and assuming there
        are no obstacles from current position to the exit point.
        """
        if direction == 'UP':
            return (0, column)

        if direction == 'DOWN':
            return (9, column)

        if direction == 'LEFT':
            return (row, 0)

        if direction == 'RIGHT':
            return (row, 9)


class Atom:
    """
    Represents an atom.
    Responsibilities: Keeps track of which atoms are left.
    Collaborator: BlackBoxGame
    """

    def __init__(self, atoms):
        """Initializes atoms by using a list of atom tuples. Creates a list to hold the atoms guessed by the player."""
        self._atoms = atoms
        self._atom_guesses = []

    def get_atoms(self):
        """Returns the atom tuples in the atom list."""
        return self._atoms

    def remove_atom(self, row, column):
        """When atom is guessed correctly, remove atom from list of atoms."""
        self._atoms.remove((row,  column))

    def get_atom_guesses(self):
        """Returns atom guesses."""
        return self._atom_guesses

    def add_to_atom_guesses(self, row, column):
        """Adds a (row,column) tuple to the list of atom guesses."""
        self._atom_guesses.append((row, column))
