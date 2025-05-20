class Diplomacy:
    def __init__(self):
        self.relations = {}  # Dicionário para armazenar relações entre civilizações
        
    def initialize_relations(self, civilizations):
        """Inicializa relações diplomáticas entre todas as civilizações."""
        for civ1 in civilizations:
            for civ2 in civilizations:
                if civ1 != civ2:
                    self.set_relation(civ1, civ2, "Paz")
    
    def set_relation(self, civ1, civ2, status):
        """Define o status diplomático entre duas civilizações."""
        key = self._get_relation_key(civ1, civ2)
        self.relations[key] = status
    
    def get_status(self, civ1, civ2):
        """Retorna o status diplomático entre duas civilizações."""
        key = self._get_relation_key(civ1, civ2)
        return self.relations.get(key, "Desconhecido")
    
    def declare_war(self, civ1, civ2):
        """Declara guerra entre duas civilizações."""
        self.set_relation(civ1, civ2, "Guerra")
    
    def make_peace(self, civ1, civ2):
        """Estabelece paz entre duas civilizações."""
        self.set_relation(civ1, civ2, "Paz")
    
    def make_alliance(self, civ1, civ2):
        """Estabelece uma aliança entre duas civilizações."""
        self.set_relation(civ1, civ2, "Aliança")
    
    def make_trade_agreement(self, civ1, civ2):
        """Estabelece um acordo comercial entre duas civilizações."""
        self.set_relation(civ1, civ2, "Acordo Comercial")
    
    def _get_relation_key(self, civ1, civ2):
        """Cria uma chave única para o par de civilizações."""
        # Ordena os IDs para garantir que (A,B) e (B,A) tenham a mesma chave
        ids = sorted([id(civ1), id(civ2)])
        return f"{ids[0]}_{ids[1]}"
    
    def process_turn(self):
        """Processa eventos diplomáticos a cada turno."""
        # Aqui poderíamos implementar mudanças aleatórias nas relações,
        # propostas de paz, etc.
        pass
