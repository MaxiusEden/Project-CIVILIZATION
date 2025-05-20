"""
Modelo para tecnologias no jogo.
"""

class Tech:
    """
    Representa uma tecnologia na árvore tecnológica.
    """
    
    def __init__(self, tech_id, data):
        """
        Inicializa uma tecnologia.
        
        Args:
            tech_id (str): Identificador único da tecnologia.
            data (dict): Dados da tecnologia.
        """
        self.id = tech_id
        self.name = data.get('name', tech_id)
        self.cost = data.get('cost', 0)
        self.era = data.get('era', 'ancient')
        self.description = data.get('description', '')
        
        # Requisitos
        self.requires = data.get('requires', [])
        
        # O que esta tecnologia desbloqueia
        self.unlocks_buildings = data.get('unlocks_buildings', [])
        self.unlocks_units = data.get('unlocks_units', [])
        self.unlocks_improvements = data.get('unlocks_improvements', [])
        self.unlocks_resources = data.get('unlocks_resources', [])
        
        # Efeitos especiais
        self.effects = data.get('effects', {})
    
    def can_research(self, researched_techs):
        """
        Verifica se esta tecnologia pode ser pesquisada.
        
        Args:
            researched_techs (list): Lista de tecnologias já pesquisadas.
            
        Returns:
            bool: True se todos os pré-requisitos foram atendidos, False caso contrário.
        """
        if not self.requires:
            return True
        
        for req in self.requires:
            if req not in researched_techs:
                return False
        
        return True
    
    def to_dict(self):
        """
        Converte a tecnologia para um dicionário.
        
        Returns:
            dict: Representação da tecnologia como dicionário.
        """
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'era': self.era,
            'description': self.description,
            'requires': self.requires,
            'unlocks_buildings': self.unlocks_buildings,
            'unlocks_units': self.unlocks_units,
            'unlocks_improvements': self.unlocks_improvements,
            'unlocks_resources': self.unlocks_resources,
            'effects': self.effects
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria uma tecnologia a partir de um dicionário.
        
        Args:
            data (dict): Dicionário com os dados da tecnologia.
            
        Returns:
            Tech: Nova instância de Tech.
        """
        tech_id = data.pop('id')
        return cls(tech_id, data)
