# game/controllers/game_controller.py
import logging
from game.models.game_state import GameState
from game.utils.save_manager import SaveManager

class GameController:
    """
    Controlador principal do jogo.
    
    Gerencia o fluxo do jogo, incluindo inicialização, turnos e interação com outros controladores.
    """
    
    def __init__(self, config=None):
        """
        Inicializa o controlador do jogo.
        
        Args:
            config (dict): Configurações do jogo.
        """
        self.game_state = None
        self.config = config or {}
        self.save_manager = SaveManager()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Referências a outros controladores
        self.world_controller = None
        self.civ_controller = None
        self.city_controller = None
        self.unit_controller = None
    
    def initialize_controllers(self):
        """Inicializa os controladores dependentes."""
        from game.controllers.world_controller import WorldController
        from game.controllers.civ_controller import CivController
        from game.controllers.city_controller import CityController
        from game.controllers.unit_controller import UnitController
        
        self.world_controller = WorldController(self)
        self.civ_controller = CivController(self)
        self.city_controller = CityController(self)
        self.unit_controller = UnitController(self)
    
    def new_game(self, config=None):
        """
        Inicia um novo jogo.
        
        Args:
            config (dict): Configurações do jogo.
            
        Returns:
            bool: True se o jogo foi iniciado com sucesso, False caso contrário.
        """
        if config:
            self.config.update(config)
        
        self.game_state = GameState(self.config)
        self.game_state.initialize_new_game()
        
        # Inicializa controladores se ainda não foram inicializados
        if not self.world_controller:
            self.initialize_controllers()
        
        self.logger.info("Novo jogo iniciado")
        return True
    
    def load_game(self, save_name):
        """
        Carrega um jogo salvo.
        
        Args:
            save_name (str): Nome do arquivo de salvamento.
            
        Returns:
            bool: True se o jogo foi carregado com sucesso, False caso contrário.
        """
        try:
            self.game_state = self.save_manager.load_game(save_name)
            
            # Inicializa controladores se ainda não foram inicializados
            if not self.world_controller:
                self.initialize_controllers()
            
            self.logger.info(f"Jogo carregado: {save_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao carregar jogo: {e}")
            return False
    
    def save_game(self, save_name):
        """
        Salva o jogo atual.
        
        Args:
            save_name (str): Nome do arquivo de salvamento.
            
        Returns:
            bool: True se o jogo foi salvo com sucesso, False caso contrário.
        """
        if not self.game_state:
            self.logger.error("Nenhum jogo ativo para salvar")
            return False
        
        try:
            self.save_manager.save_game(self.game_state, save_name)
            self.logger.info(f"Jogo salvo: {save_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar jogo: {e}")
            return False
    
    def end_turn(self):
        """
        Finaliza o turno atual e processa o próximo turno.
        
        Returns:
            dict: Resultados do processamento do turno.
        """
        if not self.game_state:
            self.logger.error("Nenhum jogo ativo")
            return {'error': 'no_active_game'}
        
        # Processa o turno
        results = self.game_state.process_turn()
        
        # Verifica se o jogo acabou
        if self.game_state.game_over:
            self.logger.info(f"Jogo terminado. Vencedor: {self.game_state.winner.name}")
            results['game_over'] = True
            results['winner'] = self.game_state.winner.name
        
        return results
    
    def get_available_saves(self):
        """
        Obtém a lista de jogos salvos disponíveis.
        
        Returns:
            list: Lista de nomes de arquivos de salvamento.
        """
        return self.save_manager.get_available_saves()
    
    def is_game_active(self):
        """
        Verifica se há um jogo ativo.
        
        Returns:
            bool: True se há um jogo ativo, False caso contrário.
        """
        return self.game_state is not None
