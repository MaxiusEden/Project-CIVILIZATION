import tkinter as tk
from tkinter import font, messagebox
import os
import sys
import importlib.util

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import tkinter
        return True
    except ImportError:
        print("Error: tkinter is not installed.")
        print("Please install tkinter to run this game.")
        return False

def create_data_directories():
    """Create necessary directories for game data."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("saves", exist_ok=True)

def create_sample_data_files():
    """Create sample data files if they don't exist."""
    import json
    
    # Technologies file
    if not os.path.exists("data/technologies.json"):
        with open("data/technologies.json", "r") as f:
            # File already exists, no need to create it
            pass
    
    # Units file
    if not os.path.exists("data/units.json"):
        with open("data/units.json", "r") as f:
            # File already exists, no need to create it
            pass
    
    # Buildings file
    if not os.path.exists("data/buildings.json"):
        with open("data/buildings.json", "r") as f:
            # File already exists, no need to create it
            pass

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project CIVILIZATION")
        self.root.geometry("800x600")
        self.root.configure(bg="black")
        
        # Create fonts
        self.title_font = font.Font(family="Arial", size=24, weight="bold")
        self.subtitle_font = font.Font(family="Arial", size=14)
        self.button_font = font.Font(family="Arial", size=12)
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Title
        tk.Label(
            self.main_frame,
            text="PROJECT CIVILIZATION",
            font=self.title_font,
            bg="black",
            fg="white"
        ).pack(pady=20)
        
        # Subtitle
        tk.Label(
            self.main_frame,
            text="A turn-based strategy game",
            font=self.subtitle_font,
            bg="black",
            fg="white"
        ).pack(pady=10)
        
        # Buttons frame
        self.button_frame = tk.Frame(self.main_frame, bg="black")
        self.button_frame.pack(pady=50)
        
        # New Game button
        tk.Button(
            self.button_frame,
            text="New Game",
            font=self.button_font,
            bg="black",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=20,
            height=2,
            command=self.start_new_game
        ).pack(pady=10)
        
        # Load Game button (disabled for now)
        tk.Button(
            self.button_frame,
            text="Load Game",
            font=self.button_font,
            bg="black",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=20,
            height=2,
            state=tk.DISABLED
        ).pack(pady=10)
        
        # Quit button
        tk.Button(
            self.button_frame,
            text="Quit",
            font=self.button_font,
            bg="black",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            width=20,
            height=2,
            command=root.destroy
        ).pack(pady=10)
    
    def start_new_game(self):
        """Start a new game."""
        # Hide the launcher window
        self.root.withdraw()
        
        # Create a new window for the game
        game_root = tk.Toplevel(self.root)
        game_root.title("Project CIVILIZATION")
        game_root.geometry("1024x768")
        
        # Import the game module
        import game.civilization_gui as civilization_gui
        
        # Start the game
        game = civilization_gui.CivilizationGame(game_root)
        
        # When the game window is closed, show the launcher again
        game_root.protocol("WM_DELETE_WINDOW", self.show_launcher)
    
    def show_launcher(self):
        """Show the launcher window again."""
        self.root.deiconify()

def main():
    """Main function to start the game launcher."""
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Create directories and sample files
    create_data_directories()
    create_sample_data_files()
    
    # Create the launcher window
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
