import tkinter as tk
from tkinter import messagebox
import random
import time


def create_board(rows, cols, num_mines, initial_click_row, initial_click_col):
    """Create a Minesweeper game board with randomly placed mines, ensuring a safe initial click.

    Args:
        rows (int): Number of rows in the game board.
        cols (int): Number of columns in the game board.
        num_mines (int): Number of mines to be placed on the game board.
        initial_click_row (int): Row index of the initially clicked cell.
        initial_click_col (int): Column index of the initially clicked cell.

    Returns:
        list: 2D list representing the Minesweeper game board.
    """
    board = [[0 for _ in range(cols)] for _ in range(rows)]

    # Get all possible positions except the initially clicked cell and its neighbors
    possible_positions = [(i, j) for i in range(rows) for j in range(cols)
                          if abs(i - initial_click_row) > 1 or abs(j - initial_click_col) > 1]

    # Randomly place mines in the remaining positions
    mine_positions = random.sample(possible_positions, num_mines)

    for position in mine_positions:
        row, col = position
        # Use a character or value to represent mines (e.g., '*')
        board[row][col] = '*'

    # Update values in neighboring cells
    for i in range(rows):
        for j in range(cols):
            if board[i][j] == '*':
                continue  # Skip mines

            # Count mines in neighboring cells
            mine_count = sum(1 for x in range(max(0, i - 1), min(rows, i + 2))
                             for y in range(max(0, j - 1), min(cols, j + 2))
                             if board[x][y] == '*')

            board[i][j] = mine_count

    return board


class MinesweeperGUI:
    """Minesweeper GUI."""

    DIFFICULTY_LEVELS = {'Beginner': {'rows': 9, 'cols': 9, 'mines': 10},
                         'Intermediate': {'rows': 16, 'cols': 16, 'mines': 40},
                         'Expert': {'rows': 16, 'cols': 30, 'mines': 99}}

    def __init__(self, master, rows, cols, num_mines):
        self.master = master
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.board = None
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flags = [[False for _ in range(cols)] for _ in range(rows)]
        self.unprobed_color = "#E0E0E0"
        self.initial_click_row = None
        self.initial_click_col = None
        self.first_click = True
        self.iteration = 0
        self.solver = False

        self.create_widgets()

        solve_button = tk.Button(
            self.master, text='Solve', command=self.activate_solver)
        restart_button = tk.Button(
            self.master, text="Restart", command=self.restart_game)

    def create_widgets(self):
        """Create GUI widgets for the Minesweeper game."""
        self.buttons = [[None for _ in range(self.cols)]
                        for _ in range(self.rows)]

        for row in range(self.rows):
            for col in range(self.cols):
                button = tk.Button(self.master, text='', width=4, height=2, font=('Arial', 10),
                                   command=lambda r=row, c=col: self.click_square(r, c))

                button.configure(bg=self.unprobed_color, fg='black')

                button.grid(row=row, column=col, padx=2, pady=2)
                button.bind('<Button-3>', lambda event, r=row,
                            c=col: self.right_click_square(r, c))
                self.buttons[row][col] = button

        # Difficulty change button
        change_difficulty_button = tk.Button(
            self.master, text='Change Difficulty', command=self.show_difficulty_menu)
        change_difficulty_button.grid(
            row=0, column=self.cols, padx=10, pady=10, sticky='w')

        # Solving button
        solve_button = tk.Button(
            self.master, text='Solve', command=self.activate_solver)
        solve_button.grid(row=1, column=self.cols,
                          padx=10, pady=10, sticky='w')

        # Restart button
        restart_button = tk.Button(
            self.master, text="Restart", command=self.restart_game)
        restart_button.grid(row=3, column=self.cols,
                            padx=10, pady=10, sticky='w')

    def show_difficulty_menu(self):
        """Show a menu to select difficulty level."""
        difficulty_menu = tk.Toplevel(self.master)
        difficulty_menu.title("Choose Difficulty")

        for difficulty, config in self.DIFFICULTY_LEVELS.items():
            button = tk.Button(difficulty_menu, text=difficulty.capitalize(),
                               command=lambda d=difficulty: self.change_difficulty(d))
            button.pack(pady=5)

    def change_difficulty(self, difficulty):
        """Change the difficulty level and reset the game."""
        if difficulty in self.DIFFICULTY_LEVELS:
            self.rows = self.DIFFICULTY_LEVELS[difficulty]['rows']
            self.cols = self.DIFFICULTY_LEVELS[difficulty]['cols']
            self.num_mines = self.DIFFICULTY_LEVELS[difficulty]['mines']

            self.master.destroy()  # Close the current window

            # Start a new game with the updated difficulty level
            root = tk.Tk()
            root.title("Minesweeper")
            game = MinesweeperGUI(root, self.rows, self.cols, self.num_mines)
            root.mainloop()
        else:
            messagebox.showwarning("Invalid Difficulty",
                                   "Please enter a valid difficulty level.")

    def click_square(self, row, col):
        """Handle a left-click on the specified square.

        Args:
            row (int): Row index of the square.
            col (int): Column index of the square.
        """
        if self.first_click:
            # Dynamically assign initial_click_row and initial_click_col on the first click
            self.initial_click_row = row
            self.initial_click_col = col

            # Use the modified create_board function with initial_click_row and initial_click_col
            self.board = create_board(self.rows, self.cols, self.num_mines,
                                      self.initial_click_row, self.initial_click_col)

            self.first_click = False

        if not self.revealed[row][col] and not self.flags[row][col]:
            if self.board[row][col] == '*':
                self.game_lose()
            else:
                mines_nearby = self.count_adjacent_mines(row, col)
                self.revealed[row][col] = True
                self.buttons[row][col].config(text=str(mines_nearby))

                # Set the background color for probed cells
                color = self.get_cell_color(mines_nearby)
                self.buttons[row][col].config(
                    state='normal', bg=color, fg='black')

                if mines_nearby == 0:
                    self.reveal_empty_squares(row, col)

                if self.check_win() and self.solver == False:
                    self.game_win()
                    return

    def right_click_square(self, row, col):
        """Handle a right-click on the specified square.

        Args:
            row (int): Row index of the square.
            col (int): Column index of the square.
        """
        if not self.revealed[row][col]:
            self.flags[row][col] = not self.flags[row][col]
            self.update_button_text(row, col)

    def reveal_cell(self, row, col):
        """Reveal the specified cell on the game board.

        Args:
            row (int): Row index of the cell.
            col (int): Column index of the cell.
        """
        if not self.revealed[row][col] and not self.flags[row][col]:
            if self.board[row][col] == '*':
                self.game_lose = True
            else:
                mines_nearby = self.count_adjacent_mines(row, col)
                self.revealed[row][col] = True

                if mines_nearby == 0:
                    self.reveal_empty_squares(row, col)

                if self.check_win():
                    self.game_win = True

    def count_adjacent_mines(self, row, col):
        """Count the number of mines adjacent to the specified square.

        Args:
            row (int): Row index of the square.
            col (int): Column index of the square.

        Returns:
            int: Number of adjacent mines.
        """
        count = 0
        rows, cols = self.rows, self.cols

        for i in range(max(0, row - 1), min(rows, row + 2)):
            for j in range(max(0, col - 1), min(cols, col + 2)):
                if self.board[i][j] == '*':
                    count += 1

        return count

    def reveal_empty_squares(self, row, col):
        """Reveal empty squares recursively starting from the specified square.

        Args:
            row (int): Row index of the square.
            col (int): Column index of the square.
        """
        for i in range(max(0, row - 1), min(self.rows, row + 2)):
            for j in range(max(0, col - 1), min(self.cols, col + 2)):
                if not self.revealed[i][j]:
                    self.click_square(i, j)

    def update_button_text(self, row, col):
        """Update the text and background color of the specified square.

        Args:
            row (int): Row index of the square.
            col (int): Column index of the square.
        """
        if self.flags[row][col]:
            self.buttons[row][col].config(text='🚩', bg='#3BD76A', fg='black')
        else:
            self.buttons[row][col].config(text='', bg=self.unprobed_color)

    def get_cell_color(self, value):
        """Determine the background color for a cell based on its value.

        Args:
            value: Value of the cell.

        Returns:
            str: Hexadecimal color code.
        """
        low_intensity_color = "#FFE3AF"  # Color for low intensity
        high_intensity_color = "#3853FF"  # Color for high intensity

        value_range = 8
        factor = value / value_range

        r_low, g_low, b_low = tuple(
            int(low_intensity_color[i:i+2], 16) for i in (1, 3, 5))
        r_high, g_high, b_high = tuple(
            int(high_intensity_color[i:i+2], 16) for i in (1, 3, 5))

        r = int(r_low + factor * (r_high - r_low))
        g = int(g_low + factor * (g_high - g_low))
        b = int(b_low + factor * (b_high - b_low))

        color = "#{:02x}{:02x}{:02x}".format(r, g, b)

        return color

    def check_win(self):
        """Check if the player has won the game.

        Returns:
            bool: True if the player has won, False otherwise.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.revealed[row][col] and self.board[row][col] != '*':
                    return False
        return True

    def show_mines(self):
        """Reveal all mines on the game board."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == '*':
                    self.buttons[row][col].config(
                        text='💣', state='disabled', bg='#2B2B2B')

    def game_lose(self):
        """Handle the end of the game when the player hits a mine."""
        self.show_mines()
        messagebox.showinfo("Game Over", "You hit a mine!")
        return True

    def game_win(self):
        """Handle the end of the game when the player wins."""
        self.show_mines()
        messagebox.showinfo(
            "You Win!", "Congratulations! You've probed every non-mine containing cell.")
        return True

    def restart_game(self):
        """
        Resets all game attributes and creates a new board.
        """
        # Reset revealed and flagged states
        for i in range(self.rows):
            for j in range(self.cols):
                self.revealed[i][j] = False
                self.flags[i][j] = False

        # Reset game state and create new board
        self.first_click = True
        self.board = None
        self.initial_click_row = None
        self.initial_click_col = None
        self.iteration = 0

        # Update button appearance and state
        for row in range(self.rows):
            for col in range(self.cols):
                self.buttons[row][col].config(
                    text="", bg=self.unprobed_color, state="normal")

    def count_unrevealed_neighbors(self, row, col):
        """
        Count the number of unrevealed neighbors around the specified cell.

        Args:
            row (int): Row index of the cell.
            col (int): Column index of the cell.

        Returns:
            int: Number of unrevealed neighbors.
        """
        count = 0
        for i in range(max(0, row - 1), min(self.rows, row + 2)):
            for j in range(max(0, col - 1), min(self.cols, col + 2)):
                if not self.revealed[i][j]:
                    count += 1

        return count

    def count_flagged_neighbors(self, row, col):
        """
        Count the number of flagged neighbors around the specified cell.

        Args:
            row (int): Row index of the cell.
            col (int): Column index of the cell.

        Returns:
            int: Number of flagged neighbors.
        """
        count = 0
        for i in range(max(0, row - 1), min(self.rows, row + 2)):
            for j in range(max(0, col - 1), min(self.cols, col + 2)):
                if self.flags[i][j]:
                    count += 1

        return count

    def has_unprobed_neighbors(self, row, col):
        """
        Check if there are unprobed neighbors around the specified cell.

        Args:
            row (int): Row index of the cell.
            col (int): Column index of the cell.

        Returns:
            bool: True if there are unprobed neighbors, False otherwise.
        """
        for i in range(max(0, row - 1), min(self.rows, row + 2)):
            for j in range(max(0, col - 1), min(self.cols, col + 2)):
                if not self.revealed[i][j] and not self.flags[i][j]:
                    return True
        return False

    def activate_solver(self):
        """
        Activate the solve_game method
        """
        self.iteration = 0
        self.solver = True
        self.solve_game()

    def solve_game(self):
        """
        Solve the game using the Single Point (SP) strategy

        This function iterates through all unrevealed cells and applies SP strategy.
        """
        stop_traversal = False

        while not stop_traversal and self.iteration < 2:
            # Store the current state of the board
            prev_board_state = [row[:] for row in self.revealed]

            for row in range(self.rows):
                for col in range(self.cols):
                    if self.revealed[row][col] and self.board[row][col] > 0 and self.has_unprobed_neighbors(row, col):
                        # Highlight the current cell
                        # self.buttons[row][col].config(bg='#FFCCE2')
                        self.master.update()
                        time.sleep(0)

                        # Check if the clicked cell is a mine
                        if self.board[row][col] == '*':
                            self.game_lose()

                        # Apply SP strategy
                        self.apply_single_point_strategy(row, col)

                        # Reset the color of the cell
                        # self.buttons[row][col].config(bg=self.unprobed_color)
                        self.master.update()

                    if stop_traversal:
                        break

            # Check for changes in the board state
            current_board_state = [row[:] for row in self.revealed]
            if current_board_state == prev_board_state:
                self.iteration += 1

        # Check for win conditions after solving
        if self.check_win():
            stop_traversal
            messagebox.showinfo(
                "Win!", "Hooray, I solved the puzzle! ╰( ⁀‿⁀ )╯")
            return
        else:
            stop_traversal
            messagebox.showinfo(
                "Solver Stopped", "Sorry, couldn't solve the whole puzzle (っ˘̩╭╮˘̩)っ")
            return

    def apply_single_point_strategy(self, row, col):
        """
        Apply the Single Point (SP) strategy to the specified cell

        Args:
            row (int): Row index of the cell.
            col (int): Column index of the cell.
        """
        unrevealed_neighbors = self.count_unrevealed_neighbors(row, col)
        flagged_neighbors = self.count_flagged_neighbors(row, col)
        cell_value = int(self.board[row][col]
                         ) if self.revealed[row][col] else 0
        remaining_unrevealed_neighbors = unrevealed_neighbors - flagged_neighbors

        # Scenario 1: Deduce safe cells
        if flagged_neighbors == cell_value:
            # All unrevealed neighbors are safe to reveal
            for i in range(max(0, row - 1), min(self.rows, row + 2)):
                for j in range(max(0, col - 1), min(self.cols, col + 2)):
                    if not self.revealed[i][j] and not self.flags[i][j]:
                        self.click_square(i, j)

        # Scenario 2: Deduce and flag mines
        elif remaining_unrevealed_neighbors == cell_value - flagged_neighbors:
            # If the number of remaining mines equals the number of unrevealed neighbors,
            # flag all unrevealed neighbors as mines.
            for i in range(max(0, row - 1), min(self.rows, row + 2)):
                for j in range(max(0, col - 1), min(self.cols, col + 2)):
                    if not self.revealed[i][j] and not self.flags[i][j]:
                        self.right_click_square(i, j)

    def solve_game_time(self):
        """
        Solve the game using the Single Point (SP) strategy (for tracking time)

        This function iterates through all unrevealed cells and applies SP strategy.
        """
        total_time = 0.0
        stop_traversal = False

        start_time = time.time()
        while not stop_traversal and self.iteration < 2:
            # Store the current state of the board
            prev_board_state = [row[:] for row in self.revealed]

            for row in range(self.rows):
                for col in range(self.cols):
                    if self.revealed[row][col] and self.board[row][col] > 0 and self.has_unprobed_neighbors(row, col):
                        # Highlight the current cell
                        # self.buttons[row][col].config(bg='#FFCCE2')
                        self.master.update()
                        time.sleep(0)

                        # Check if the clicked cell is a mine
                        if self.board[row][col] == '*':
                            self.game_lose()

                        # Apply SP strategy
                        self.apply_single_point_strategy(row, col)

                        # Reset the color of the cell
                        # self.buttons[row][col].config(bg=self.unprobed_color)
                        self.master.update()

                    if stop_traversal:
                        break

            # Check for changes in the board state
            current_board_state = [row[:] for row in self.revealed]
            if current_board_state == prev_board_state:
                self.iteration += 1

        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        total_time += elapsed_time

        # Check for win conditions after solving
        if self.check_win():
            stop_traversal
            print(total_time)
            self.master.destroy()
        else:
            stop_traversal
            print(total_time)
            self.master.destroy()

    def activate_first_click(self):
        """
        Randomly choose first click on the grid and start the game.
        """
        self.iteration = 0
        self.solver = True

        # Randomly select a cell to click
        initial_click_row = random.randint(0, self.rows - 1)
        initial_click_col = random.randint(0, self.cols - 1)

        # Perform the initial click to start the game
        self.click_square(initial_click_row, initial_click_col)

        # Start the solver
        self.solve_game_time()
