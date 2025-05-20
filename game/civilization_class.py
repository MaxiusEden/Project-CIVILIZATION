import random
from game.unit import Unit
from game.city import City
from game.tech import Technology, TechTree

class Civilization:
    def __init__(self, name, leader):
        self.name = name
        self.leader = leader
        self.cities = []
        self.units = []
        self.technologies = []
        self.researching = None
        self.research_progress = 0
        self.gold = 100
        self.science = 0
        self.culture = 0
        self.happiness = 0
        self.era = "Antiga"
        self.world = None
        self.tech_tree = TechTree()
    
    def create_unit(self, unit_type, position):
        """Creates a new unit of the specified type."""
        unit = Unit(unit_type, self, position)
        self.units.append(unit)
        if self.world:
            self.world.units.append(unit)
        return unit
    
    def found_city(self, name, position):
        """Founds a new city at the specified position."""
        city = City(name, self, position)
        self.cities.append(city)
        if self.world:
            self.world.cities.append(city)
        return city
    
    def process_turn(self):
        """Processes a turn for the civilization."""
        # Calculate income
        self.gold += self.calculate_income()
        
        # Calculate science
        self.science = self.calculate_science()
        
        # Process research
        if self.researching:
            self.research_progress += self.science
            if self.research_progress >= self.researching.cost:
                self.technologies.append(self.researching)
                self.researching = None
                self.research_progress = 0
    
    def calculate_income(self):
        """Calculates the civilization's income for this turn."""
        base_income = 5  # Base income per turn
        city_income = sum(city.gold_per_turn for city in self.cities)
        unit_maintenance = sum(unit.maintenance for unit in self.units)
        
        return base_income + city_income - unit_maintenance
    
    def calculate_science(self):
        """Calculates the civilization's science output for this turn."""
        base_science = 1  # Base science per turn
        city_science = sum(city.science_per_turn for city in self.cities)
        
        return base_science + city_science
    
    def start_research(self, tech_name):
        """Starts researching a new technology."""
        if self.researching:
            return False
        
        # Find the technology in the tech tree
        if tech_name in self.tech_tree.technologies:
            tech = self.tech_tree.technologies[tech_name]
            
            # Check if we can research this technology
            if tech.is_available([t for t in self.technologies]):
                self.researching = tech
                self.research_progress = 0
                return True
        
        return False
    
    def has_technology(self, tech_name):
        """Checks if the civilization has researched a specific technology."""
        return any(tech.name == tech_name for tech in self.technologies)
    
    def get_available_technologies(self):
        """Returns a list of technologies available for research."""
        return self.tech_tree.get_available_techs(self.technologies)
    
    def declare_war(self, target_civ):
        """Declares war on another civilization."""
        if self.world and self.world.diplomacy:
            self.world.diplomacy.declare_war(self, target_civ)
    
    def make_peace(self, target_civ):
        """Makes peace with another civilization."""
        if self.world and self.world.diplomacy:
            self.world.diplomacy.make_peace(self, target_civ)
