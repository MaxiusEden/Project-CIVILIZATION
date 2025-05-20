import tkinter as tk
from tkinter import font, messagebox, simpledialog
import random
from game.world import World
from game.civilization_class import Civilization
from game.diplomacy import Diplomacy
import os
import sys

# Add the parent directory to the path so we can import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import game modules
from game.world import World
from game.civilization_class import Civilization
from game.diplomacy import Diplomacy

class TkRenderer:
    """Tkinter-based renderer for the game"""
    
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="black")
        
        # Create fonts
        self.default_font = font.Font(family="Arial", size=10)
        self.bold_font = font.Font(family="Arial", size=10, weight="bold")
        self.title_font = font.Font(family="Arial", size=12, weight="bold")
        
        # Create main frames
        self.map_frame = tk.Frame(root, bg="black")
        self.map_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.status_frame = tk.Frame(root, bg="black")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Create map canvas
        self.map_canvas = tk.Canvas(self.map_frame, bg="black", highlightthickness=0)
        self.map_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create status labels
        self.status_label = tk.Label(self.status_frame, text="", bg="black", fg="white", font=self.default_font, anchor=tk.W)
        self.status_label.pack(side=tk.TOP, fill=tk.X)
        
        self.research_label = tk.Label(self.status_frame, text="", bg="black", fg="white", font=self.default_font, anchor=tk.W)
        self.research_label.pack(side=tk.TOP, fill=tk.X)
        
        # Create command buttons
        self.cmd_frame = tk.Frame(self.status_frame, bg="black")
        self.cmd_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # Initialize callbacks to None
        self.next_turn_callback = None
        self.city_menu_callback = None
        self.tech_tree_callback = None
        self.unit_command_callback = None
        self.diplomacy_callback = None
        self.quit_callback = None
        
        # Create buttons (they'll be connected to callbacks later)
        self.buttons = []
        button_texts = ["Next Turn (n)", "Cities (c)", "Tech Tree (t)", "Units (u)", "Diplomacy (d)", "Quit (q)"]
        
        for text in button_texts:
            btn = tk.Button(
                self.cmd_frame,
                text=text,
                bg="black",
                fg="white",
                activebackground="#555555",
                activeforeground="white",
                font=self.default_font
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons.append(btn)
    
    def set_callbacks(self, next_turn, city_menu, tech_tree, unit_command, diplomacy, quit_game):
        """Set the callback functions for the buttons"""
        self.next_turn_callback = next_turn
        self.city_menu_callback = city_menu
        self.tech_tree_callback = tech_tree
        self.unit_command_callback = unit_command
        self.diplomacy_callback = diplomacy
        self.quit_callback = quit_game
        
        # Connect buttons to callbacks
        self.buttons[0].config(command=self.next_turn_callback)
        self.buttons[1].config(command=self.city_menu_callback)
        self.buttons[2].config(command=self.tech_tree_callback)
        self.buttons[3].config(command=self.unit_command_callback)
        self.buttons[4].config(command=self.diplomacy_callback)
        self.buttons[5].config(command=self.quit_callback)
    
    def render_world(self, world, center_x=None, center_y=None):
        """Render the game world on the canvas"""
        # Clear the canvas
        self.map_canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.map_canvas.winfo_width()
        canvas_height = self.map_canvas.winfo_height()
        
        # If canvas hasn't been drawn yet, use default size
        if canvas_width <= 1:
            canvas_width = 600
        if canvas_height <= 1:
            canvas_height = 400
        
        # Determine the center of the view
        if center_x is None or center_y is None:
            center_x = world.width // 2
            center_y = world.height // 2
        
        # Calculate tile size
        tile_size = min(canvas_width // world.width, canvas_height // world.height)
        
        # Calculate the visible area
        visible_width = canvas_width // tile_size
        visible_height = canvas_height // tile_size
        
        start_x = max(0, center_x - visible_width // 2)
        start_y = max(0, center_y - visible_height // 2)
        
        end_x = min(world.width, start_x + visible_width)
        end_y = min(world.height, start_y + visible_height)
        
        # Define colors for different terrain types
        colors = {
            '.': "#7CFC00",  # Light green for plains
            '~': "#1E90FF",  # Blue for water
            '^': "#A9A9A9",  # Gray for mountains
            '#': "#228B22",  # Forest green for forests
            '*': "#FFD700"   # Gold for resources
        }
        
        # Draw the map
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = (x - start_x) * tile_size
                screen_y = (y - start_y) * tile_size
                
                # Get tile type and color
                tile = world.get_tile(x, y)
                color = colors.get(tile, "black")
                
                # Draw the tile
                self.map_canvas.create_rectangle(
                    screen_x, screen_y, 
                    screen_x + tile_size, screen_y + tile_size,
                    fill=color, outline="#333333"
                )
                
                # Draw a symbol for the tile type
                symbol = tile
                self.map_canvas.create_text(
                    screen_x + tile_size // 2,
                    screen_y + tile_size // 2,
                    text=symbol,
                    fill="black"
                )
        
        # Draw cities
        for city in world.cities:
            x, y = city.position
            screen_x = (x - start_x) * tile_size + tile_size // 2
            screen_y = (y - start_y) * tile_size + tile_size // 2
            
            if start_x <= x < end_x and start_y <= y < end_y:
                # Draw city as a circle
                self.map_canvas.create_oval(
                    screen_x - tile_size // 3, screen_y - tile_size // 3,
                    screen_x + tile_size // 3, screen_y + tile_size // 3,
                    fill="red", outline="white"
                )
                
                # Draw city name
                self.map_canvas.create_text(
                    screen_x, screen_y - tile_size // 2 - 5,
                    text=city.name,
                    fill="white",
                    font=self.default_font
                )
        
        # Draw units
        for unit in world.units:
            x, y = unit.position
            screen_x = (x - start_x) * tile_size + tile_size // 2
            screen_y = (y - start_y) * tile_size + tile_size // 2
            
            if start_x <= x < end_x and start_y <= y < end_y:
                # Draw unit as a square
                self.map_canvas.create_rectangle(
                    screen_x - tile_size // 4, screen_y - tile_size // 4,
                    screen_x + tile_size // 4, screen_y + tile_size // 4,
                    fill="purple", outline="white"
                )
                
                # Draw unit symbol
                self.map_canvas.create_text(
                    screen_x, screen_y,
                    text=unit.symbol,
                    fill="white",
                    font=self.bold_font
                )
    
    def render_status(self, civilization, turn):
        """Render status information"""
        # Update status label
        status_text = f"Turn: {turn} | {civilization.name} | Era: {civilization.era} | Gold: {civilization.gold} | Science: {civilization.science}/turn"
        self.status_label.config(text=status_text)
        
        # Update research label
        if civilization.researching:
            research_text = f"Researching: {civilization.researching.name} ({civilization.research_progress}/{civilization.researching.cost})"
        else:
            research_text = "No current research"
        self.research_label.config(text=research_text)
    
    def city_menu(self, civilization):
        """Menu for city management"""
        # Create a new window
        city_window = tk.Toplevel(self.root)
        city_window.title("City Management")
        city_window.geometry("600x400")
        city_window.configure(bg="black")
        
        if not civilization.cities:
            tk.Label(city_window, text="You don't have any cities.", bg="black", fg="white", font=self.bold_font).pack(pady=20)
            tk.Button(city_window, text="Close", command=city_window.destroy, bg="black", fg="white").pack(pady=10)
            return
        
        # Create a frame for the city list
        city_frame = tk.Frame(city_window, bg="black")
        city_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(city_frame, text="Your Cities", bg="black", fg="white", font=self.bold_font).pack(anchor=tk.W)
        
        city_listbox = tk.Listbox(
            city_frame, 
            bg="black", 
            fg="white", 
            selectbackground="#555555",
            font=self.default_font,
            height=15
        )
        city_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add cities to the listbox
        for city in civilization.cities:
            city_listbox.insert(tk.END, f"{city.name} (Pop: {city.population})")
        
        # Create a frame for city details
        detail_frame = tk.Frame(city_window, bg="black")
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        detail_text = tk.Text(
            detail_frame,
            bg="black",
            fg="white",
            font=self.default_font,
            wrap=tk.WORD,
            height=15,
            width=40
        )
        detail_text.pack(fill=tk.BOTH, expand=True)
        detail_text.config(state=tk.DISABLED)
        
        # Function to display city details
        def show_city_details(event):
            selection = city_listbox.curselection()
            if selection:
                index = selection[0]
                city = civilization.cities[index]
                
                detail_text.config(state=tk.NORMAL)
                detail_text.delete(1.0, tk.END)
                
                detail_text.insert(tk.END, city.get_status_string())
                
                detail_text.config(state=tk.DISABLED)
                
                # Enable action buttons
                build_btn.config(state=tk.NORMAL)
                unit_btn.config(state=tk.NORMAL)
        
        city_listbox.bind('<<ListboxSelect>>', show_city_details)
        
        # Buttons for city actions
        btn_frame = tk.Frame(detail_frame, bg="black")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Function to open building menu
        def open_building_menu():
            selection = city_listbox.curselection()
            if selection:
                index = selection[0]
                city = civilization.cities[index]
                self.building_menu(city)
                # Update the city details after building selection
                show_city_details(None)
        
        # Function to open unit production menu
        def open_unit_menu():
            selection = city_listbox.curselection()
            if selection:
                index = selection[0]
                city = civilization.cities[index]
                self.unit_production_menu(city)
                # Update the city details after unit selection
                show_city_details(None)
        
        build_btn = tk.Button(
            btn_frame,
            text="Build",
            command=open_building_menu,
            bg="black",
            fg="white",
            state=tk.DISABLED
        )
        build_btn.pack(side=tk.LEFT, padx=5)
        
        unit_btn = tk.Button(
            btn_frame,
            text="Produce Unit",
            command=open_unit_menu,
            bg="black",
            fg="white",
            state=tk.DISABLED
        )
        unit_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(
            btn_frame,
            text="Close",
            command=city_window.destroy,
            bg="black",
            fg="white"
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Make the window modal
        city_window.transient(self.root)
        city_window.grab_set()
        self.root.wait_window(city_window)
    
    def building_menu(self, city):
        """Menu for building selection"""
        # Create a new window
        build_window = tk.Toplevel(self.root)
        build_window.title(f"Build in {city.name}")
        build_window.geometry("500x400")
        build_window.configure(bg="black")
        
        # Get available buildings
        available_buildings = self._get_available_buildings(city)
        
        if not available_buildings:
            tk.Label(build_window, text="No buildings available for construction.", bg="black", fg="white", font=self.bold_font).pack(pady=20)
            tk.Button(build_window, text="Close", command=build_window.destroy, bg="black", fg="white").pack(pady=10)
            return
        
        # Create a listbox for buildings
        tk.Label(build_window, text="Available Buildings:", bg="black", fg="white", font=self.bold_font).pack(anchor=tk.W, padx=10, pady=5)
        
        building_frame = tk.Frame(build_window, bg="black")
        building_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        building_listbox = tk.Listbox(
            building_frame, 
            bg="black", 
            fg="white", 
            selectbackground="#555555",
            font=self.default_font,
            height=10
        )
        building_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add buildings to the listbox
        for building in available_buildings:
            building_listbox.insert(tk.END, f"{building.name} (Cost: {building.cost})")
        
        # Create a text widget for building description
        description_text = tk.Text(
            building_frame,
            bg="black",
            fg="white",
            font=self.default_font,
            wrap=tk.WORD,
            height=10,
            width=30
        )
        description_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        description_text.config(state=tk.DISABLED)
        
        # Function to display building description
        def show_building_description(event):
            selection = building_listbox.curselection()
            if selection:
                index = selection[0]
                building = available_buildings[index]
                
                description_text.config(state=tk.NORMAL)
                description_text.delete(1.0, tk.END)
                
                description_text.insert(tk.END, building.description)
                description_text.insert(tk.END, "\n\nEffects:\n")
                
                for effect, value in building.effects.items():
                    description_text.insert(tk.END, f"- {effect.capitalize()}: +{value}\n")
                
                description_text.config(state=tk.DISABLED)
        
        building_listbox.bind('<<ListboxSelect>>', show_building_description)
        
        # Buttons
        btn_frame = tk.Frame(build_window, bg="black")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        def build_selected():
            selection = building_listbox.curselection()
            if selection:
                index = selection[0]
                building = available_buildings[index]
                success = city.queue_building(building.building_type)
                
                if success:
                    messagebox.showinfo("Building", f"{building.name} added to production queue.")
                    build_window.destroy()
                else:
                    messagebox.showerror("Error", "Cannot build this building.")
        
        build_btn = tk.Button(
            btn_frame,
            text="Build",
            command=build_selected,
            bg="black",
            fg="white"
        )
        build_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=build_window.destroy,
            bg="black",
            fg="white"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        # Make the window modal
        build_window.transient(self.root)
        build_window.grab_set()
        self.root.wait_window(build_window)
    
    def _get_available_buildings(self, city):
        """Return a list of buildings available for construction"""
        from game.building import Building
        
        # List of basic building types
        building_types = ["granary", "monument", "library", "barracks", "walls", "market", "water_mill"]
        
        available = []
        for building_type in building_types:
            building = Building(building_type)
            if building.can_be_built(city, city.civilization.technologies):
                available.append(building)
                
        return available
    
    def unit_production_menu(self, city):
        """Menu for unit production"""
        # Create a new window
        unit_window = tk.Toplevel(self.root)
        unit_window.title(f"Produce Units in {city.name}")
        unit_window.geometry("500x400")
        unit_window.configure(bg="black")
        
        # Get available units
        available_units = self._get_available_units(city)
        
        if not available_units:
            tk.Label(unit_window, text="No units available for production.", bg="black", fg="white", font=self.bold_font).pack(pady=20)
            tk.Button(unit_window, text="Close", command=unit_window.destroy, bg="black", fg="white").pack(pady=10)
            return
        
        # Create a listbox for units
        tk.Label(unit_window, text="Available Units:", bg="black", fg="white", font=self.bold_font).pack(anchor=tk.W, padx=10, pady=5)
        
        unit_frame = tk.Frame(unit_window, bg="black")
        unit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        unit_listbox = tk.Listbox(
            unit_frame, 
            bg="black", 
            fg="white", 
            selectbackground="#555555",
            font=self.default_font,
            height=10
        )
        unit_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add units to the listbox
        unit_types = list(available_units.keys())
        for unit_type in unit_types:
            data = available_units[unit_type]
            unit_listbox.insert(tk.END, f"{data['name']} (Cost: {data['cost']})")
        
        # Create a text widget for unit description
        description_text = tk.Text(
            unit_frame,
            bg="black",
            fg="white",
            font=self.default_font,
            wrap=tk.WORD,
            height=10,
            width=30
        )
        description_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        description_text.config(state=tk.DISABLED)
        
        # Function to display unit description
        def show_unit_description(event):
            selection = unit_listbox.curselection()
            if selection:
                index = selection[0]
                unit_type = unit_types[index]
                data = available_units[unit_type]
                
                description_text.config(state=tk.NORMAL)
                description_text.delete(1.0, tk.END)
                
                if 'description' in data:
                    description_text.insert(tk.END, data['description'] + "\n\n")
                
                description_text.insert(tk.END, f"Combat Strength: {data.get('combat_strength', 0)}\n")
                description_text.insert(tk.END, f"Movement: {data.get('movement', 2)}\n")
                
                if 'ranged_strength' in data:
                    description_text.insert(tk.END, f"Ranged Strength: {data['ranged_strength']}\n")
                    description_text.insert(tk.END, f"Range: {data.get('range', 2)}\n")
                
                if 'abilities' in data and data['abilities']:
                    description_text.insert(tk.END, "\nAbilities:\n")
                    for ability in data['abilities']:
                        description_text.insert(tk.END, f"- {ability}\n")
                
                description_text.config(state=tk.DISABLED)
        
        unit_listbox.bind('<<ListboxSelect>>', show_unit_description)
        
        # Buttons
        btn_frame = tk.Frame(unit_window, bg="black")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        def produce_selected():
            selection = unit_listbox.curselection()
            if selection:
                index = selection[0]
                unit_type = unit_types[index]
                success = city.queue_unit(unit_type)
                
                if success:
                    messagebox.showinfo("Production", f"{available_units[unit_type]['name']} added to production queue.")
                    unit_window.destroy()
                else:
                    messagebox.showerror("Error", "Cannot produce this unit.")
        
        produce_btn = tk.Button(
            btn_frame,
            text="Produce",
            command=produce_selected,
            bg="black",
            fg="white"
        )
        produce_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=unit_window.destroy,
            bg="black",
            fg="white"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=10)
        
        # Make the window modal
        unit_window.transient(self.root)
        unit_window.grab_set()
        self.root.wait_window(unit_window)
    
    def _get_available_units(self, city):
        """Return a dictionary of units available for production"""
        import json
        
        try:
            with open('data/units.json', 'r') as f:
                units_data = json.load(f)
                
            # Filter units based on available technologies
            available_units = {}
            for unit_type, data in units_data.items():
                required_tech = data.get('requires_tech')
                if required_tech is None or city.civilization.has_technology(required_tech):
                    available_units[unit_type] = data
                    
            return available_units
        except (FileNotFoundError, json.JSONDecodeError):
            # Return basic units if the file is not found
            return {
                "settler": {"name": "Colonizador", "cost": 80},
                "warrior": {"name": "Guerreiro", "cost": 40},
                "builder": {"name": "Construtor", "cost": 50}
            }
    
    def tech_tree(self, civilization):
        """Technology tree interface"""
        # Create a new window
        tech_window = tk.Toplevel(self.root)
        tech_window.title("Technology Tree")
        tech_window.geometry("600x500")
        tech_window.configure(bg="black")
        
        # Create frames
        left_frame = tk.Frame(tech_window, bg="black")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = tk.Frame(tech_window, bg="black")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Current research
        current_frame = tk.LabelFrame(left_frame, text="Current Research", bg="black", fg="white", font=self.bold_font)
        current_frame.pack(fill=tk.X, pady=10)
        
        if civilization.researching:
            research_text = f"{civilization.researching.name}\nProgress: {civilization.research_progress}/{civilization.researching.cost}"
            progress_percent = min(100, int(civilization.research_progress / civilization.researching.cost * 100))
            
            tk.Label(current_frame, text=research_text, bg="black", fg="white").pack(pady=5)
            
            # Progress bar
            progress_frame = tk.Frame(current_frame, bg="black")
            progress_frame.pack(fill=tk.X, padx=10, pady=5)
            
            progress_bar = tk.Canvas(progress_frame, height=20, bg="black", highlightthickness=0)
            progress_bar.pack(fill=tk.X)
            
            # Draw progress bar
            bar_width = progress_frame.winfo_width()
            if bar_width <= 1:
                bar_width = 200  # Default width if not yet rendered
            
            progress_bar.create_rectangle(0, 0, bar_width, 20, fill="black", outline="white")
            progress_bar.create_rectangle(0, 0, bar_width * progress_percent / 100, 20, fill="#4CAF50", outline="")
            
            progress_bar.create_text(bar_width / 2, 10, text=f"{progress_percent}%", fill="white")
        else:
            tk.Label(current_frame, text="No current research", bg="black", fg="white").pack(pady=5)
        
        # Researched technologies
        researched_frame = tk.LabelFrame(left_frame, text="Researched Technologies", bg="black", fg="white", font=self.bold_font)
        researched_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        researched_listbox = tk.Listbox(
            researched_frame, 
            bg="black", 
            fg="white", 
            selectbackground="#555555",
            font=self.default_font,
            height=10
        )
        researched_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add researched technologies to the listbox
        if civilization.technologies:
            for tech in civilization.technologies:
                researched_listbox.insert(tk.END, tech.name)
        else:
            researched_listbox.insert(tk.END, "No technologies researched yet")
        
        # Available technologies
        available_frame = tk.LabelFrame(right_frame, text="Available Technologies", bg="black", fg="white", font=self.bold_font)
        available_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        available_techs = civilization.get_available_technologies()
        
        available_listbox = tk.Listbox(
            available_frame, 
            bg="black", 
            fg="white", 
            selectbackground="#555555",
            font=self.default_font,
            height=15
        )
        available_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add available technologies to the listbox
        if available_techs:
            for tech in available_techs:
                available_listbox.insert(tk.END, f"{tech.name} (Cost: {tech.cost})")
        else:
            available_listbox.insert(tk.END, "No technologies available for research")
        
        # Description frame
        desc_frame = tk.LabelFrame(right_frame, text="Description", bg="black", fg="white", font=self.bold_font)
        desc_frame.pack(fill=tk.X, pady=10)
        
        desc_text = tk.Text(
            desc_frame,
            bg="black",
            fg="white",
            font=self.default_font,
            wrap=tk.WORD,
            height=6,
            width=30
        )
        desc_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        desc_text.config(state=tk.DISABLED)
        
        # Function to display technology description
        def show_tech_description(event):
            selection = available_listbox.curselection()
            if selection:
                index = selection[0]
                if available_techs:
                    tech = available_techs[index]
                    
                    desc_text.config(state=tk.NORMAL)
                    desc_text.delete(1.0, tk.END)
                    
                    if hasattr(tech, 'description'):
                        desc_text.insert(tk.END, tech.description + "\n\n")
                    
                    desc_text.insert(tk.END, f"Era: {tech.era}\n")
                    
                    if tech.prerequisites:
                        desc_text.insert(tk.END, "\nPrerequisites:\n")
                        for prereq in tech.prerequisites:
                            desc_text.insert(tk.END, f"- {prereq}\n")
                    
                    if tech.unlocks:
                        desc_text.insert(tk.END, "\nUnlocks:\n")
                        for unlock in tech.unlocks:
                            desc_text.insert(tk.END, f"- {unlock}\n")
                    
                    desc_text.config(state=tk.DISABLED)
        
        available_listbox.bind('<<ListboxSelect>>', show_tech_description)
        
        # Buttons
        btn_frame = tk.Frame(tech_window, bg="black")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        def research_selected():
            selection = available_listbox.curselection()
            if selection:
                index = selection[0]
                if available_techs:
                    tech = available_techs[index]
                    civilization.start_research(tech.name)
                    messagebox.showinfo("Research", f"Started researching {tech.name}.")
                    tech_window.destroy()
        
        research_btn = tk.Button(
            btn_frame,
            text="Research Selected Technology",
            command=research_selected,
            bg="black",
            fg="white"
        )
        research_btn.pack(side=tk.LEFT, padx=10)
        
        close_btn = tk.Button(
            btn_frame,
            text="Close",
            command=tech_window.destroy,
            bg="black",
            fg="white"
        )
        close_btn.pack(side=tk.RIGHT, padx=10)
        
        # Make the window modal
        tech_window.transient(self.root)
        tech_window.grab_set()
        self.root.wait_window(tech_window)
    
    def unit_command_menu(self, civilization):
        """Interface for commanding units"""
        # Create a new window
        unit_window = tk.Toplevel(self.root)
        unit_window.title("Unit Commands")
        unit_window.geometry("600x400")
        unit_window.configure(bg="black")
        
        if not civilization.units:
            tk.Label(unit_window, text="You don't have any units.", bg="black", fg="white", font=self.bold_font).pack(pady=20)
            tk.Button(unit_window, text="Close", command=unit_window.destroy, bg="black", fg="white").pack(pady=10)
            return
        
        # Create frames
        left_frame = tk.Frame(unit_window, bg="black")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = tk.Frame(unit_window, bg="black")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Unit list
        tk.Label(left_frame, text="Your Units", bg="black", fg="white", font=self.bold_font).pack(anchor=tk.W)
        
        unit_listbox = tk.Listbox(
            left_frame, 
            bg="black", 
            fg="white", 
            selectbackground="#555555",
            font=self.default_font,
            height=15
        )
        unit_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add units to the listbox
        for unit in civilization.units:
            unit_listbox.insert(tk.END, f"{unit.name} ({unit.position[0]}, {unit.position[1]}) - Moves: {unit.moves_left}/{unit.max_moves}")
        
        # Unit details
        detail_frame = tk.LabelFrame(right_frame, text="Unit Details", bg="black", fg="white", font=self.bold_font)
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        detail_text = tk.Text(
            detail_frame,
            bg="black",
            fg="white",
            font=self.default_font,
            wrap=tk.WORD,
            height=10,
            width=30
        )
        detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        detail_text.config(state=tk.DISABLED)
        
        # Action buttons
        action_frame = tk.Frame(right_frame, bg="black")
        action_frame.pack(fill=tk.X, pady=10)
        
        move_btn = tk.Button(
            action_frame,
            text="Move",
            bg="black",
            fg="white",
            state=tk.DISABLED
        )
        move_btn.pack(side=tk.LEFT, padx=5)
        
        found_btn = tk.Button(
            action_frame,
            text="Found City",
            bg="black",
            fg="white",
            state=tk.DISABLED
        )
        found_btn.pack(side=tk.LEFT, padx=5)
        
        build_btn = tk.Button(
            action_frame,
            text="Build",
            bg="black",
            fg="white",
            state=tk.DISABLED
        )
        build_btn.pack(side=tk.LEFT, padx=5)
        
        attack_btn = tk.Button(
            action_frame,
            text="Attack",
            bg="black",
            fg="white",
            state=tk.DISABLED
        )
        attack_btn.pack(side=tk.LEFT, padx=5)
        
        # Selected unit reference
        selected_unit = [None]  # Using a list to store reference that can be modified in nested functions
        
        # Function to display unit details
        def show_unit_details(event):
            selection = unit_listbox.curselection()
            if selection:
                index = selection[0]
                unit = civilization.units[index]
                selected_unit[0] = unit
                
                detail_text.config(state=tk.NORMAL)
                detail_text.delete(1.0, tk.END)
                
                detail_text.insert(tk.END, f"Name: {unit.name}\n")
                detail_text.insert(tk.END, f"Position: ({unit.position[0]}, {unit.position[1]})\n")
                detail_text.insert(tk.END, f"Health: {unit.health}/100\n")
                detail_text.insert(tk.END, f"Moves: {unit.moves_left}/{unit.max_moves}\n")
                
                if hasattr(unit, 'combat_strength') and unit.combat_strength > 0:
                    detail_text.insert(tk.END, f"Combat Strength: {unit.combat_strength}\n")
                
                if hasattr(unit, 'ranged_strength') and unit.ranged_strength > 0:
                    detail_text.insert(tk.END, f"Ranged Strength: {unit.ranged_strength}\n")
                    detail_text.insert(tk.END, f"Range: {unit.range}\n")
                
                if unit.abilities:
                    detail_text.insert(tk.END, "\nAbilities:\n")
                    for ability in unit.abilities:
                        detail_text.insert(tk.END, f"- {ability}\n")
                
                detail_text.config(state=tk.DISABLED)
                
                # Enable/disable action buttons based on unit capabilities
                move_btn.config(state=tk.NORMAL if unit.moves_left > 0 else tk.DISABLED)
                found_btn.config(state=tk.NORMAL if 'found_city' in unit.abilities and unit.moves_left > 0 else tk.DISABLED)
                build_btn.config(state=tk.NORMAL if 'build_improvement' in unit.abilities and unit.moves_left > 0 else tk.DISABLED)
                attack_btn.config(state=tk.NORMAL if hasattr(unit, 'combat_strength') and unit.combat_strength > 0 and unit.moves_left > 0 else tk.DISABLED)
        
        unit_listbox.bind('<<ListboxSelect>>', show_unit_details)
        
        # Move unit function
        def move_unit():
            unit = selected_unit[0]
            if unit and unit.moves_left > 0:
                move_window = tk.Toplevel(unit_window)
                move_window.title(f"Move {unit.name}")
                move_window.geometry("300x200")
                move_window.configure(bg="black")
                
                tk.Label(move_window, text=f"Current position: ({unit.position[0]}, {unit.position[1]})", bg="black", fg="white").pack(pady=10)
                tk.Label(move_window, text="Choose direction:", bg="black", fg="white").pack(pady=5)
                
                dir_frame = tk.Frame(move_window, bg="black")
                dir_frame.pack(pady=10)
                
                # Direction buttons
                tk.Button(
                    dir_frame, text="↑", width=3, height=1, 
                    command=lambda: move_in_direction(0, -1),
                    bg="black", fg="white"
                ).grid(row=0, column=1)
                
                tk.Button(
                    dir_frame, text="←", width=3, height=1, 
                    command=lambda: move_in_direction(-1, 0),
                    bg="black", fg="white"
                ).grid(row=1, column=0)
                
                tk.Button(
                    dir_frame, text="→", width=3, height=1, 
                    command=lambda: move_in_direction(1, 0),
                    bg="black", fg="white"
                ).grid(row=1, column=2)
                
                tk.Button(
                    dir_frame, text="↓", width=3, height=1, 
                    command=lambda: move_in_direction(0, 1),
                    bg="black", fg="white"
                ).grid(row=2, column=1)
                
                result_label = tk.Label(move_window, text="", bg="black", fg="white")
                result_label.pack(pady=10)
                
                def move_in_direction(dx, dy):
                    success = unit.move(dx, dy)
                    if success:
                        result_label.config(text=f"Moved to ({unit.position[0]}, {unit.position[1]})")
                        # Update the unit list
                        unit_listbox.delete(unit_listbox.curselection()[0])
                        unit_listbox.insert(unit_listbox.curselection()[0], 
                                          f"{unit.name} ({unit.position[0]}, {unit.position[1]}) - Moves: {unit.moves_left}/{unit.max_moves}")
                        # Update unit details
                        show_unit_details(None)
                        
                        if unit.moves_left <= 0:
                            move_window.destroy()
                    else:
                        result_label.config(text="Cannot move in that direction")
                
                tk.Button(
                    move_window, text="Close", 
                    command=move_window.destroy,
                    bg="black", fg="white"
                ).pack(pady=5)
                
                # Make the window modal
                move_window.transient(unit_window)
                move_window.grab_set()
                unit_window.wait_window(move_window)
        
        # Found city function
        def found_city():
            unit = selected_unit[0]
            if unit and 'found_city' in unit.abilities and unit.moves_left > 0:
                city_name = simpledialog.askstring("Found City", "Enter city name:", parent=unit_window)
                if city_name:
                    if unit.found_city():
                        messagebox.showinfo("City Founded", f"{city_name} has been founded!")
                        # Refresh unit list
                        unit_listbox.delete(0, tk.END)
                        for u in civilization.units:
                            unit_listbox.insert(tk.END, f"{u.name} ({u.position[0]}, {u.position[1]}) - Moves: {u.moves_left}/{u.max_moves}")
                        # Clear selection
                        selected_unit[0] = None
                        detail_text.config(state=tk.NORMAL)
                        detail_text.delete(1.0, tk.END)
                        detail_text.config(state=tk.DISABLED)
                        # Disable buttons
                        move_btn.config(state=tk.DISABLED)
                        found_btn.config(state=tk.DISABLED)
                        build_btn.config(state=tk.DISABLED)
                        attack_btn.config(state=tk.DISABLED)
                    else:
                        messagebox.showerror("Error", "Could not found city here.")
        
        # Build improvement function
        def build_improvement():
            unit = selected_unit[0]
            if unit and 'build_improvement' in unit.abilities and unit.moves_left > 0:
                build_window = tk.Toplevel(unit_window)
                build_window.title("Build Improvement")
                build_window.geometry("300x200")
                build_window.configure(bg="black")
                
                tk.Label(build_window, text="Select improvement to build:", bg="black", fg="white").pack(pady=10)
                
                improvements = [
                    ("farm", "Farm"),
                    ("mine", "Mine"),
                    ("pasture", "Pasture"),
                    ("plantation", "Plantation"),
                    ("camp", "Camp")
                ]
                
                imp_var = tk.StringVar(build_window)
                imp_var.set(improvements[0][0])
                
                for imp_id, imp_name in improvements:
                    tk.Radiobutton(
                        build_window, 
                        text=imp_name, 
                        variable=imp_var, 
                        value=imp_id,
                        bg="black", 
                        fg="white", 
                        selectcolor="black"
                    ).pack(anchor=tk.W, padx=20)
                
                def build_selected():
                    imp_id = imp_var.get()
                    success = unit.build_improvement(imp_id)
                    if success:
                        messagebox.showinfo("Improvement", f"{dict(improvements)[imp_id]} built successfully!")
                        build_window.destroy()
                        
                        # Refresh unit list if the builder was consumed
                        if unit not in civilization.units:
                            unit_listbox.delete(0, tk.END)
                            for u in civilization.units:
                                unit_listbox.insert(tk.END, f"{u.name} ({u.position[0]}, {u.position[1]}) - Moves: {u.moves_left}/{u.max_moves}")
                            # Clear selection
                            selected_unit[0] = None
                            detail_text.config(state=tk.NORMAL)
                            detail_text.delete(1.0, tk.END)
                            detail_text.config(state=tk.DISABLED)
                            # Disable buttons
                            move_btn.config(state=tk.DISABLED)
                            found_btn.config(state=tk.DISABLED)
                            build_btn.config(state=tk.DISABLED)
                            attack_btn.config(state=tk.DISABLED)
                        else:
                            # Update the unit details
                            show_unit_details(None)
                    else:
                        messagebox.showerror("Error", "Could not build improvement.")
                
                btn_frame = tk.Frame(build_window, bg="black")
                btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
                
                tk.Button(
                    btn_frame, text="Build", 
                    command=build_selected,
                    bg="black", fg="white"
                ).pack(side=tk.LEFT, padx=10)
                
                tk.Button(
                    btn_frame, text="Cancel", 
                    command=build_window.destroy,
                    bg="black", fg="white"
                ).pack(side=tk.RIGHT, padx=10)
                
                # Make the window modal
                build_window.transient(unit_window)
                build_window.grab_set()
                unit_window.wait_window(build_window)
        
        # Attack function
        def attack_target():
            unit = selected_unit[0]
            if unit and unit.combat_strength > 0 and unit.moves_left > 0:
                # Find potential targets
                targets = []
                attack_range = unit.range if hasattr(unit, 'range') and unit.range > 0 else 1
                
                for target in unit.civilization.world.units:
                    if target.civilization != unit.civilization:
                        tx, ty = target.position
                        ux, uy = unit.position
                        distance = max(abs(tx - ux), abs(ty - uy))
                        
                        if distance <= attack_range:
                            targets.append(target)
                
                if not targets:
                    messagebox.showinfo("Attack", "No targets in range.")
                    return
                
                # Create attack window
                attack_window = tk.Toplevel(unit_window)
                attack_window.title("Attack Target")
                attack_window.geometry("400x300")
                attack_window.configure(bg="black")
                
                tk.Label(attack_window, text="Select target to attack:", bg="black", fg="white").pack(pady=10)
                
                target_listbox = tk.Listbox(
                    attack_window, 
                    bg="black", 
                    fg="white", 
                    selectbackground="#555555",
                    font=self.default_font,
                    height=10
                )
                target_listbox.pack(fill=tk.BOTH, expand=True, padx=10)
                
                # Add targets to the listbox
                for target in targets:
                    target_listbox.insert(tk.END, f"{target.name} ({target.position[0]}, {target.position[1]}) - Health: {target.health}/100")
                
                def attack_selected():
                    selection = target_listbox.curselection()
                    if selection:
                        index = selection[0]
                        target = targets[index]
                        success = unit.attack(target)
                        
                        if success:
                            messagebox.showinfo("Attack", f"Attack successful! Target health: {target.health}/100")
                            attack_window.destroy()
                            
                            # Update unit details
                            show_unit_details(None)
                            
                            # If target was destroyed, refresh the target list
                            if target.health <= 0:
                                messagebox.showinfo("Victory", f"Enemy {target.name} has been defeated!")
                        else:
                            messagebox.showerror("Error", "Attack failed.")
                
                btn_frame = tk.Frame(attack_window, bg="black")
                btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
                
                tk.Button(
                    btn_frame, text="Attack", 
                    command=attack_selected,
                    bg="black", fg="white"
                ).pack(side=tk.LEFT, padx=10)
                
                tk.Button(
                    btn_frame, text="Cancel", 
                    command=attack_window.destroy,
                    bg="black", fg="white"
                ).pack(side=tk.RIGHT, padx=10)
                
                # Make the window modal
                attack_window.transient(unit_window)
                attack_window.grab_set()
                unit_window.wait_window(attack_window)
        
        # Connect action buttons to functions
        move_btn.config(command=move_unit)
        found_btn.config(command=found_city)
        build_btn.config(command=build_improvement)
        attack_btn.config(command=attack_target)
        
        # Close button
        close_btn = tk.Button(
            right_frame,
            text="Close",
            command=unit_window.destroy,
            bg="black",
            fg="white"
        )
        close_btn.pack(side=tk.BOTTOM, pady=10)
        
        # Make the window modal
        unit_window.transient(self.root)
        unit_window.grab_set()
        self.root.wait_window(unit_window)
    
    def diplomacy_menu(self, civilization):
        """Diplomacy interface"""
        # Create a new window
        diplo_window = tk.Toplevel(self.root)
        diplo_window.title("Diplomacy")
        diplo_window.geometry("500x400")
        diplo_window.configure(bg="black")
        
        # Get other civilizations
        other_civs = [civ for civ in civilization.world.civilizations if civ != civilization]
        
        if not other_civs:
            tk.Label(diplo_window, text="No other civilizations known.", bg="black", fg="white", font=self.bold_font).pack(pady=20)
            tk.Button(diplo_window, text="Close", command=diplo_window.destroy, bg="black", fg="white").pack(pady=10)
            return
        
        # Create frames
        left_frame = tk.Frame(diplo_window, bg="black")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = tk.Frame(diplo_window, bg="black")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Civilization list
        tk.Label(left_frame, text="Civilizations", bg="black", fg="white", font=self.bold_font).pack(anchor=tk.W)
        
        civ_listbox = tk.Listbox(
            left_frame, 
            bg="black", 
            fg="white", 
            selectbackground="#555555",
            font=self.default_font,
            height=15
        )
        civ_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add civilizations to the listbox
        for civ in other_civs:
            status = civilization.world.diplomacy.get_status(civilization, civ)
            civ_listbox.insert(tk.END, f"{civ.name} ({civ.leader}) - {status}")
        
        # Diplomacy actions
        action_frame = tk.LabelFrame(right_frame, text="Diplomatic Actions", bg="black", fg="white", font=self.bold_font)
        action_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Selected civilization reference
        selected_civ = [None]  # Using a list to store reference that can be modified in nested functions
        
        # Function to update available actions
        def update_actions():
            # Clear previous buttons
            for widget in action_frame.winfo_children():
                widget.destroy()
            
            if not selected_civ[0]:
                return
            
            target_civ = selected_civ[0]
            status = civilization.world.diplomacy.get_status(civilization, target_civ)
            
            if status == "Guerra":
                tk.Button(
                    action_frame,
                    text="Propose Peace",
                    command=lambda: propose_peace(target_civ),
                    bg="black",
                    fg="white"
                ).pack(fill=tk.X, padx=10, pady=5)
            else:
                tk.Button(
                    action_frame,
                    text="Declare War",
                    command=lambda: declare_war(target_civ),
                    bg="black",
                    fg="white"
                ).pack(fill=tk.X, padx=10, pady=5)
                
                tk.Button(
                    action_frame,
                    text="Propose Trade Agreement",
                    command=lambda: propose_trade(target_civ),
                    bg="black",
                    fg="white"
                ).pack(fill=tk.X, padx=10, pady=5)
                
                tk.Button(
                    action_frame,
                    text="Propose Alliance",
                    command=lambda: propose_alliance(target_civ),
                    bg="black",
                    fg="white"
                ).pack(fill=tk.X, padx=10, pady=5)
        
        # Function to display civilization details
        def show_civ_details(event):
            selection = civ_listbox.curselection()
            if selection:
                index = selection[0]
                target_civ = other_civs[index]
                selected_civ[0] = target_civ
                
                # Update available actions
                update_actions()
        
        civ_listbox.bind('<<ListboxSelect>>', show_civ_details)
        
        # Diplomatic action functions
        def declare_war(target_civ):
            if messagebox.askyesno("Declare War", f"Are you sure you want to declare war on {target_civ.name}?"):
                civilization.declare_war(target_civ)
                messagebox.showinfo("War Declared", f"You are now at war with {target_civ.name}!")
                
                # Update the listbox
                selection = civ_listbox.curselection()[0]
                civ_listbox.delete(selection)
                civ_listbox.insert(selection, f"{target_civ.name} ({target_civ.leader}) - Guerra")
                civ_listbox.selection_set(selection)
                
                # Update available actions
                update_actions()
        
        def propose_peace(target_civ):
            if messagebox.askyesno("Propose Peace", f"Do you want to propose peace to {target_civ.name}?"):
                # In a real game, this might involve negotiations or conditions
                civilization.make_peace(target_civ)
                messagebox.showinfo("Peace Agreement", f"Peace has been established with {target_civ.name}.")
                
                # Update the listbox
                selection = civ_listbox.curselection()[0]
                civ_listbox.delete(selection)
                civ_listbox.insert(selection, f"{target_civ.name} ({target_civ.leader}) - Paz")
                civ_listbox.selection_set(selection)
                
                # Update available actions
                update_actions()
        
        def propose_trade(target_civ):
            # In a real game, this would open a trade negotiation window
            messagebox.showinfo("Trade Agreement", f"{target_civ.name} has accepted your trade agreement!")
            
            # Update the listbox
            selection = civ_listbox.curselection()[0]
            civ_listbox.delete(selection)
            civ_listbox.insert(selection, f"{target_civ.name} ({target_civ.leader}) - Acordo Comercial")
            civ_listbox.selection_set(selection)
            
            # Update diplomatic status
            civilization.world.diplomacy.make_trade_agreement(civilization, target_civ)
            
            # Update available actions
            update_actions()
        
        def propose_alliance(target_civ):
            # In a real game, this might involve conditions or prerequisites
            messagebox.showinfo("Alliance", f"{target_civ.name} has accepted your alliance proposal!")
            
            # Update the listbox
            selection = civ_listbox.curselection()[0]
            civ_listbox.delete(selection)
            civ_listbox.insert(selection, f"{target_civ.name} ({target_civ.leader}) - Aliança")
            civ_listbox.selection_set(selection)
            
            # Update diplomatic status
            civilization.world.diplomacy.make_alliance(civilization, target_civ)
            
            # Update available actions
            update_actions()
        
        # Close button
        close_btn = tk.Button(
            right_frame,
            text="Close",
            command=diplo_window.destroy,
            bg="black",
            fg="white"
        )
        close_btn.pack(side=tk.BOTTOM, pady=10)
        
        # Make the window modal
        diplo_window.transient(self.root)
        diplo_window.grab_set()
        self.root.wait_window(diplo_window)


class CivilizationGame:
    """Main game class that replaces the curses-based main function"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Project CIVILIZATION")
        self.root.geometry("800x600")
        self.root.configure(bg="black")
        
        # Create the renderer
        self.renderer = TkRenderer(root)
        
        # Set up the game
        self.setup_game()
        
        # Set up callbacks
        self.renderer.set_callbacks(
            self.next_turn,
            self.city_menu,
            self.tech_tree,
            self.unit_command,
            self.diplomacy,
            self.quit_game
        )
        
        # Initial render
        self.update_display()
        
        # Set up keyboard shortcuts
        self.root.bind('n', lambda e: self.next_turn())
        self.root.bind('c', lambda e: self.city_menu())
        self.root.bind('t', lambda e: self.tech_tree())
        self.root.bind('u', lambda e: self.unit_command())
        self.root.bind('d', lambda e: self.diplomacy())
        self.root.bind('q', lambda e: self.quit_game())
    
    def setup_game(self):
        """Set up the initial game state"""
        # Create the world
        self.world = World(width=40, height=20)
        # Note: We don't need to call generate() as the map is generated in the __init__ method
        # Remove this line: self.world.generate()
        
        # Create diplomacy
        self.diplomacy = Diplomacy()
        self.world.diplomacy = self.diplomacy
        
        # Create civilizations
        self.player_civ = Civilization("Roma", "César")
        self.ai_civ1 = Civilization("Grécia", "Péricles")
        self.ai_civ2 = Civilization("Egito", "Cleópatra")
        
        # Add civilizations to the world
        self.world.civilizations = [self.player_civ, self.ai_civ1, self.ai_civ2]
        self.player_civ.world = self.world
        self.ai_civ1.world = self.world
        self.ai_civ2.world = self.world
        
        # Initialize diplomatic relations
        self.diplomacy.initialize_relations(self.world.civilizations)
        
        # Create initial units
        self.player_settler = self.player_civ.create_unit("settler", (random.randint(5, 15), random.randint(5, 10)))
        self.player_warrior = self.player_civ.create_unit("warrior", (self.player_settler.position[0] + 1, self.player_settler.position[1]))
        
        self.ai_civ1.create_unit("settler", (random.randint(25, 35), random.randint(5, 10)))
        self.ai_civ2.create_unit("settler", (random.randint(15, 25), random.randint(10, 15)))
        
        # Game variables
        self.turn = 1
        self.game_running = True

    
    def update_display(self):
        """Update the game display"""
        # Render the world centered on player's settler
        self.renderer.render_world(self.world, self.player_settler.position[0], self.player_settler.position[1])
        
        # Render status information
        self.renderer.render_status(self.player_civ, self.turn)
    
    def next_turn(self):
        """Process the next turn"""
        # Process turn for all civilizations
        for civ in self.world.civilizations:
            civ.process_turn()
            for city in civ.cities:
                city.process_turn()
            for unit in civ.units:
                unit.process_turn()
        
        # Process diplomacy
        self.diplomacy.process_turn()
        
        # Increment turn counter
        self.turn += 1
        
        # Update the display
        self.update_display()
    
    def city_menu(self):
        """Open the city management menu"""
        self.renderer.city_menu(self.player_civ)
        self.update_display()
    
    def tech_tree(self):
        """Open the technology tree menu"""
        self.renderer.tech_tree(self.player_civ)
        self.update_display()
    
    def unit_command(self):
        """Open the unit command menu"""
        self.renderer.unit_command_menu(self.player_civ)
        self.update_display()
    
    def diplomacy(self):
        """Open the diplomacy menu"""
        self.renderer.diplomacy_menu(self.player_civ)
        self.update_display()
    
    def quit_game(self):
        """Quit the game with confirmation"""
        if messagebox.askyesno("Quit Game", "Are you sure you want to quit?"):
            self.root.destroy()
