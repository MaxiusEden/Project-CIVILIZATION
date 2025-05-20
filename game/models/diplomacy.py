"""
Modelo para diplomacia entre civilizações.
"""

class DiplomaticRelation:
    """
    Representa a relação diplomática entre duas civilizações.
    """
    
    # Níveis de relação diplomática
    LEVELS = ['war', 'unfriendly', 'neutral', 'friendly', 'allied']
    
    def __init__(self, civ1_id, civ2_id, level='neutral'):
        """
        Inicializa uma relação diplomática.
        
        Args:
            civ1_id (str): ID da primeira civilização.
            civ2_id (str): ID da segunda civilização.
            level (str): Nível inicial da relação.
        """
        self.civ1_id = civ1_id
        self.civ2_id = civ2_id
        self.level = level
        self.score = self._level_to_score(level)
        
        # Acordos ativos
        self.agreements = {
            'peace_treaty': False,
            'open_borders': False,
            'defensive_pact': False,
            'research_agreement': False,
            'trade_route': False
        }
        
        # Histórico de interações
        self.history = []
    
    def _level_to_score(self, level):
        """
        Converte um nível de relação para um valor numérico.
        
        Args:
            level (str): Nível de relação.
            
        Returns:
            int: Valor numérico correspondente.
        """
        try:
            return self.LEVELS.index(level) * 25 - 50  # -50 a 50
        except ValueError:
            return 0  # Neutro por padrão
    
    def _score_to_level(self, score):
        """
        Converte um valor numérico para um nível de relação.
        
        Args:
            score (int): Valor numérico.
            
        Returns:
            str: Nível de relação correspondente.
        """
        # Limita o score entre -50 e 50
        clamped_score = max(-50, min(50, score))
        
        # Converte para índice (0 a 4)
        index = (clamped_score + 50) // 25
        
        return self.LEVELS[index]
    
    def change_score(self, amount):
        """
        Altera a pontuação da relação.
        
        Args:
            amount (int): Quantidade a ser adicionada/subtraída.
            
        Returns:
            bool: True se o nível de relação mudou, False caso contrário.
        """
        old_level = self.level
        self.score += amount
        
        # Limita o score entre -50 e 50
        self.score = max(-50, min(50, self.score))
        
        # Atualiza o nível com base no novo score
        self.level = self._score_to_level(self.score)
        
        return old_level != self.level
    
    def declare_war(self):
        """
        Declara guerra entre as civilizações.
        
        Returns:
            bool: True se a guerra foi declarada, False se já estavam em guerra.
        """
        if self.level == 'war':
            return False
        
        self.level = 'war'
        self.score = self._level_to_score('war')
        
        # Cancela todos os acordos
        for key in self.agreements:
            self.agreements[key] = False
        
        # Registra no histórico
        self.add_history_event('war_declared')
        
        return True
    
    def make_peace(self):
        """
        Estabelece a paz entre as civilizações.
        
        Returns:
            bool: True se a paz foi estabelecida, False se já estavam em paz.
        """
        if self.level != 'war':
            return False
        
        self.level = 'unfriendly'
        self.score = self._level_to_score('unfriendly')
        
        # Ativa o tratado de paz
        self.agreements['peace_treaty'] = True
        
        # Registra no histórico
        self.add_history_event('peace_treaty')
        
        return True
    
    def add_history_event(self, event_type, details=None):
        """
        Adiciona um evento ao histórico de relações.
        
        Args:
            event_type (str): Tipo de evento.
            details (dict, optional): Detalhes adicionais do evento.
        """
        from datetime import datetime
        
        event = {
            'type': event_type,
            'turn': None,  # Será preenchido pelo controlador
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.history.append(event)
    
    def to_dict(self):
        """
        Converte a relação diplomática para um dicionário.
        
        Returns:
            dict: Representação da relação como dicionário.
        """
        return {
            'civ1_id': self.civ1_id,
            'civ2_id': self.civ2_id,
            'level': self.level,
            'score': self.score,
            'agreements': self.agreements.copy(),
            'history': self.history.copy()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria uma relação diplomática a partir de um dicionário.
        
        Args:
            data (dict): Dicionário com os dados da relação.
            
        Returns:
            DiplomaticRelation: Nova instância de DiplomaticRelation.
        """
        relation = cls(data['civ1_id'], data['civ2_id'], data['level'])
        relation.score = data['score']
        relation.agreements = data['agreements']
        relation.history = data['history']
        return relation


class DiplomacyManager:
    """
    Gerencia as relações diplomáticas entre todas as civilizações.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de diplomacia.
        """
        self.relations = {}  # Dicionário de relações: (civ1_id, civ2_id) -> DiplomaticRelation
    
    def get_relation(self, civ1_id, civ2_id):
        """
        Obtém a relação diplomática entre duas civilizações.
        
        Args:
            civ1_id (str): ID da primeira civilização.
            civ2_id (str): ID da segunda civilização.
            
        Returns:
            DiplomaticRelation: Relação entre as civilizações.
        """
        # Garante que a chave seja sempre ordenada para consistência
        key = tuple(sorted([civ1_id, civ2_id]))
        
        if key not in self.relations:
            self.relations[key] = DiplomaticRelation(key[0], key[1])
        
        return self.relations[key]
    
    def set_relation_level(self, civ1_id, civ2_id, level):
        """
        Define o nível de relação entre duas civilizações.
        
        Args:
            civ1_id (str): ID da primeira civilização.
            civ2_id (str): ID da segunda civilização.
            level (str): Novo nível de relação.
            
        Returns:
            bool: True se o nível foi alterado, False caso contrário.
        """
        relation = self.get_relation(civ1_id, civ2_id)
        old_level = relation.level
        
        relation.level = level
        relation.score = relation._level_to_score(level)
        
        return old_level != level
    
    def change_relation_score(self, civ1_id, civ2_id, amount):
        """
        Altera a pontuação da relação entre duas civilizações.
        
        Args:
            civ1_id (str): ID da primeira civilização.
            civ2_id (str): ID da segunda civilização.
            amount (int): Quantidade a ser adicionada/subtraída.
            
        Returns:
            bool: True se o nível de relação mudou, False caso contrário.
        """
        relation = self.get_relation(civ1_id, civ2_id)
        return relation.change_score(amount)
    
    def declare_war(self, civ1_id, civ2_id):
        """
        Declara guerra entre duas civilizações.
        
        Args:
            civ1_id (str): ID da primeira civilização.
            civ2_id (str): ID da segunda civilização.
            
        Returns:
            bool: True se a guerra foi declarada, False se já estavam em guerra.
        """
        relation = self.get_relation(civ1_id, civ2_id)
        return relation.declare_war()
    
    def make_peace(self, civ1_id, civ2_id):
        """
        Estabelece a paz entre duas civilizações.
        
        Args:
            civ1_id (str): ID da primeira civilização.
            civ2_id (str): ID da segunda civilização.
            
        Returns:
            bool: True se a paz foi estabelecida, False se já estavam em paz.
        """
        relation = self.get_relation(civ1_id, civ2_id)
        return relation.make_peace()
    
    def set_agreement(self, civ1_id, civ2_id, agreement_type, value=True):
        """
        Define um acordo entre duas civilizações.
        
        Args:
            civ1_id (str): ID da primeira civilização.
            civ2_id (str): ID da segunda civilização.
            agreement_type (str): Tipo de acordo.
            value (bool): Status do acordo (ativo/inativo).
            
        Returns:
            bool: True se o acordo foi alterado, False caso contrário.
        """
        relation = self.get_relation(civ1_id, civ2_id)
        
        if agreement_type not in relation.agreements:
            return False
        
        old_value = relation.agreements[agreement_type]
        relation.agreements[agreement_type] = value
        
        if old_value != value:
            relation.add_history_event(
                'agreement_changed',
                {'type': agreement_type, 'active': value}
            )
        
        return old_value != value
    
    def to_dict(self):
        """
        Converte o gerenciador de diplomacia para um dicionário.
        
        Returns:
            dict: Representação do gerenciador como dicionário.
        """
        return {
            'relations': {
                f"{k[0]}_{k[1]}": v.to_dict() 
                for k, v in self.relations.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria um gerenciador de diplomacia a partir de um dicionário.
        
        Args:
            data (dict): Dicionário com os dados do gerenciador.
            
        Returns:
            DiplomacyManager: Nova instância de DiplomacyManager.
        """
        manager = cls()
        
        for key, value in data.get('relations', {}).items():
            civ1_id, civ2_id = key.split('_')
            relation = DiplomaticRelation.from_dict(value)
            manager.relations[(civ1_id, civ2_id)] = relation
        
        return manager
