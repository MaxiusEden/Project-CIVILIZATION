import json

class Technology:
    def __init__(self, name, cost, prerequisites=None):
        self.name = name
        self.cost = cost
        self.prerequisites = prerequisites if prerequisites else []
        self.unlocks = []  # Unidades, edifícios, etc. que são desbloqueados
        self.era = self._determine_era()
        
    def _determine_era(self):
        """Determina a era da tecnologia com base no custo."""
        if self.cost < 100:
            return "Antiga"
        elif self.cost < 250:
            return "Clássica"
        elif self.cost < 500:
            return "Medieval"
        elif self.cost < 1000:
            return "Renascentista"
        elif self.cost < 1500:
            return "Industrial"
        elif self.cost < 2000:
            return "Moderna"
        else:
            return "Informação"
    
    def is_available(self, researched_techs):
        """Verifica se a tecnologia está disponível para pesquisa."""
        if not self.prerequisites:
            return True
            
        # Verifica se todos os pré-requisitos foram pesquisados
        return all(prereq in [tech.name for tech in researched_techs] for prereq in self.prerequisites)


class TechTree:
    def __init__(self):
        self.technologies = {}
        self._load_tech_tree()
        
    def _load_tech_tree(self):
        """Carrega a árvore tecnológica a partir de um arquivo JSON."""
        try:
            with open('data/technologies.json', 'r') as f:
                tech_data = json.load(f)
                
            for tech_name, data in tech_data.items():
                tech = Technology(
                    tech_name,
                    data.get('cost', 100),
                    data.get('prerequisites', [])
                )
                tech.unlocks = data.get('unlocks', [])
                self.technologies[tech_name] = tech
                
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não for encontrado, cria uma árvore tecnológica básica
            self._create_basic_tech_tree()
    
    def _create_basic_tech_tree(self):
        """Cria uma árvore tecnológica básica."""
        # Era Antiga
        self.technologies["agriculture"] = Technology("Agriculture", 50)
        self.technologies["animal_husbandry"] = Technology("Animal Husbandry", 60)
        self.technologies["mining"] = Technology("Mining", 60)
        self.technologies["sailing"] = Technology("Sailing", 70)
        self.technologies["pottery"] = Technology("Pottery", 50)
        self.technologies["archery"] = Technology("Archery", 70, ["animal_husbandry"])
        self.technologies["bronze_working"] = Technology("Bronze Working", 80, ["mining"])
        
        # Era Clássica
        self.technologies["writing"] = Technology("Writing", 120, ["pottery"])
        self.technologies["masonry"] = Technology("Masonry", 110, ["mining"])
        self.technologies["wheel"] = Technology("Wheel", 100, ["animal_husbandry"])
        self.technologies["currency"] = Technology("Currency", 140, ["writing"])
        self.technologies["horseback_riding"] = Technology("Horseback Riding", 130, ["animal_husbandry"])
        self.technologies["iron_working"] = Technology("Iron Working", 150, ["bronze_working"])
        
        # Era Medieval
        self.technologies["mathematics"] = Technology("Mathematics", 250, ["writing", "wheel"])
        self.technologies["construction"] = Technology("Construction", 230, ["masonry"])
        self.technologies["engineering"] = Technology("Engineering", 280, ["mathematics", "construction"])
        self.technologies["metal_casting"] = Technology("Metal Casting", 270, ["iron_working"])
        self.technologies["theology"] = Technology("Theology", 300, ["writing"])
        
        # Adiciona desbloqueios
        self.technologies["archery"].unlocks = ["archer"]
        self.technologies["animal_husbandry"].unlocks = ["pasture"]
        self.technologies["mining"].unlocks = ["mine"]
        self.technologies["bronze_working"].unlocks = ["spearman"]
        self.technologies["iron_working"].unlocks = ["swordsman"]
        self.technologies["horseback_riding"].unlocks = ["horseman"]
        self.technologies["masonry"].unlocks = ["walls"]
        self.technologies["pottery"].unlocks = ["granary"]
        self.technologies["writing"].unlocks = ["library"]
        self.technologies["wheel"].unlocks = ["water_mill"]
        self.technologies["currency"].unlocks = ["market"]
    
    def get_available_techs(self, researched_techs):
        """Retorna todas as tecnologias disponíveis para pesquisa."""
        available = []
        for tech_name, tech in self.technologies.items():
            # Verifica se a tecnologia já foi pesquisada
            if tech_name in [t.name for t in researched_techs]:
                continue
                
            # Verifica se a tecnologia está disponível
            if tech.is_available(researched_techs):
                available.append(tech)
                
        return available
