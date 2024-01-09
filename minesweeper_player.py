import tkinter as tk
from tkinter import messagebox
import minesweeper_gui as gui


def play_game_gui():
    """Start the Minesweeper game with GUI."""
    root = tk.Tk()
    root.title("Minesweeper")

    # Create Minesweeper game with the default difficulty
    rows = gui.MinesweeperGUI.DIFFICULTY_LEVELS['Beginner']['rows']
    cols = gui.MinesweeperGUI.DIFFICULTY_LEVELS['Beginner']['cols']
    num_mines = gui.MinesweeperGUI.DIFFICULTY_LEVELS['Beginner']['mines']

    game = gui.MinesweeperGUI(root, rows, cols, num_mines)
    root.mainloop()


def play_game_time():
    """
    Start the Minesweeper game with GUI. (for tracking time)
    
    Change the level in the code below (default Beginner, options: Intermediate, Expert)
    """
    root = tk.Tk()
    root.title("Minesweeper")

    root.attributes('-fullscreen', True)

    # Create Minesweeper game with the default difficulty
    rows = gui.MinesweeperGUI.DIFFICULTY_LEVELS['Beginner']['rows']
    cols = gui.MinesweeperGUI.DIFFICULTY_LEVELS['Beginner']['cols']
    num_mines = gui.MinesweeperGUI.DIFFICULTY_LEVELS['Beginner']['mines']

    game = gui.MinesweeperGUI(root, rows, cols, num_mines)
    root.mainloop()


if __name__ == "__main__":
    play_game_gui()

    # for i in range(30):
    #    play_game_time()

    # Average time for Beginner 65.2ms       (86 ms max)
    # Average time for Intermediate 96.2ms   (193.7ms if not stuck early, 225 ms max)
    # Average time for Expert 132.7ms        (303.2ms if not stuck early, 430 ms max)
