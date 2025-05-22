"""
Controlador principal do jogo que coordena outros controladores especializados.
"""
from PyQt5.QtCore import QObject, pyqtSignal
import logging
from typing import Dict, List, Optional, Any, Tuple, Union

# Importações de modelos
from game.models.game_state import GameState
from game.models.world import World

# Importações de controladores
from game.controllers.world_controller import WorldController
from game.controllers.civ_controller import CivController
from game.controllers.city_controller import CityController
from game.controllers.unit_controller import UnitController
from game.controllers.turn_controller import TurnController
from game.controllers.tech_controller import TechController
from game.controllers.event_controller import EventController

# Importações de utilidades
from game.utils.data_loader import DataLoader
from game.utils.save_manager import SaveManager
from game.utils.event_bus import EventBus


class GameController(QObject):
    """
    Controlador principal que coordena outros controladores especializados.
    Implementa o padrão Facade para simplificar a interface com o restante do sistema.
    """
    
    # Sinais para atualizações da GUI
    game_started = pyqtSignal()
    turn_ended = pyqtSignal()
    game_loaded = pyqtSignal()
    game_saved = pyqtSignal()
    turn_changed = pyqtSignal()
    active_city_changed = pyqtSignal()
    map_updated = pyqtSignal()
    
    def __init__(self, data_loader: Optional[DataLoader] = None, 
                 save_manager: Optional[SaveManager] = None):
        """
        Inicializa o controlador principal do jogo.
        
        Args:
            data_loader: Carregador de dados (opcional, será criado se não fornecido)
            save_manager: Gerenciador de salvamentos (opcional, será criado se não fornecido)
        """
        super().__init__()
        
        # Configurar logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Inicializando GameController")
        
        # Inicializar barramento de eventos
        self.event_bus = EventBus()
        
        # Inicializar utilitários com injeção de dependência
        self.data_loader = data_loader or DataLoader()
        self.save_manager = save_manager or SaveManager()
        
        # Carregar configuração
        self.config = self.data_loader.load_config()
        
        # Inicializar estado do jogo
        self.game_state = None
        
        # Inicializar controladores (serão criados quando um jogo for iniciado)
        self.world_controller = None
        self.civ_controller = None
        self.city_controller = None
        self.unit_controller = None
        self.turn_controller = None
        self.tech_controller = None
        self.event_controller = None
        
        # Configurar autosave
        self.autosave_interval = self.config.get('autosave_interval', 5)  # turnos
        self.autosave_enabled = self.config.get('autosave_enabled', True)
        self.autosave_slots = self.config.get('autosave_slots', 3)
    
    def new_game(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Inicia um novo jogo com a configuração fornecida.
        
        Args:
            config: Configuração do jogo (opcional, usa a configuração padrão se não fornecida)
        """
        self.logger.info("Iniciando novo jogo")
        
        # Usar configuração fornecida ou padrão
        if config is None:
            config = self.config.get('default_game', {})
        
        # Criar novo estado de jogo
        self.game_state = GameState()
        self.game_state.current_turn = 1

        # Criar o mundo
        world_size = config.get('world_size', 'standard')
        world_type = config.get('world_type', 'continents')
        world_config = self.config.get('world_sizes', {}).get(world_size, {})
        width = world_config.get('width', 40)
        height = world_config.get('height', 24)
        self.game_state.world = World(width, height)

        # Inicializar controladores com injeção de dependência
        self._initialize_controllers()

        # Gerar o mundo
        self.world_controller.generate_world(world_type)
        
        # Criar civilizações
        num_civs = config.get('num_civs', 4)
        player_civ_id = config.get('player_civ', 'rome')
        
        self.civ_controller.create_civilizations(num_civs, player_civ_id)
        
        # Posicionar unidades e cidades iniciais
        self.civ_controller.place_initial_units()
        
        # Definir civilização do jogador
        self.game_state.player_civ = self.civ_controller.get_player_civilization()
        
        # Configurar eventos iniciais
        self.event_controller.setup_initial_events()
        
        # Emitir sinal para a GUI
        self.game_started.emit()
        self.logger.info("Novo jogo iniciado com sucesso")
    
    def _initialize_controllers(self) -> None:
        """Inicializa todos os controladores especializados."""
        self.logger.debug("Inicializando controladores especializados")
        
        # Criar controladores com injeção de dependência
        self.world_controller = WorldController(self.game_state, self.event_bus)
        self.civ_controller = CivController(self, self.event_bus)
        self.city_controller = CityController(self, self.event_bus)
        self.unit_controller = UnitController(self, self.event_bus)
        self.turn_controller = TurnController(self, self.event_bus)
        self.tech_controller = TechController(self, self.event_bus)
        self.event_controller = EventController(self, self.event_bus)
        
        # Conectar sinais do barramento de eventos
        self._connect_event_signals()
    
    def _connect_event_signals(self) -> None:
        """Conecta sinais do barramento de eventos aos handlers apropriados."""
        # Exemplo de conexão de eventos
        self.event_bus.subscribe("turn.ended", self._on_turn_ended)
        self.event_bus.subscribe("city.selected", self._on_city_selected)
        self.event_bus.subscribe("map.updated", self._on_map_updated)
        self.event_bus.subscribe("game.save_requested", self._on_save_requested)
    
    def _on_turn_ended(self, data: Dict[str, Any]) -> None:
        """Handler para o evento de fim de turno."""
        self.turn_ended.emit()
        
        # Verificar se é hora de fazer autosave
        if (self.autosave_enabled and 
            self.game_state.current_turn % self.autosave_interval == 0):
            self._do_autosave()
    
    def _on_city_selected(self, data: Dict[str, Any]) -> None:
        """Handler para o evento de seleção de cidade."""
        self.active_city_changed.emit()
    
    def _on_map_updated(self, data: Dict[str, Any]) -> None:
        """Handler para o evento de atualização do mapa."""
        self.map_updated.emit()
    
    def _on_save_requested(self, data: Dict[str, Any]) -> None:
        """Handler para o evento de solicitação de salvamento."""
        save_name = data.get("save_name", "quicksave")
        self.save_game(save_name)
    
    def _do_autosave(self) -> None:
        """Realiza o autosave do jogo."""
        self.logger.info(f"Realizando autosave (turno {self.game_state.current_turn})")
        
        # Criar nome do autosave baseado no turno atual
        save_name = f"autosave_{self.game_state.current_turn}"
        
        # Salvar o jogo
        self.save_game(save_name, is_autosave=True)
        
        # Gerenciar slots de autosave (manter apenas os mais recentes)
        self._manage_autosave_slots()
    
    def _manage_autosave_slots(self) -> None:
        """Gerencia os slots de autosave, mantendo apenas os mais recentes."""
        autosaves = self.save_manager.list_autosaves()
        
        # Se temos mais autosaves que o número de slots, remover os mais antigos
        if len(autosaves) > self.autosave_slots:
            # Ordenar por data (mais antigos primeiro)
            autosaves.sort(key=lambda x: x.get('timestamp', ''))
            
            # Remover os mais antigos
            for i in range(len(autosaves) - self.autosave_slots):
                self.save_manager.delete_save(autosaves[i]['filename'])
                self.logger.debug(f"Removido autosave antigo: {autosaves[i]['filename']}")
    
    def load_game(self, save_name: str) -> bool:
        """
        Carrega um jogo salvo.
        
        Args:
            save_name: Nome do arquivo de salvamento
            
        Returns:
            True se o carregamento foi bem-sucedido, False caso contrário
        """
        self.logger.info(f"Carregando jogo: {save_name}")
        
        try:
            # Carregar estado do jogo do arquivo
            loaded_state = self.save_manager.load_game(save_name)
            
            if not loaded_state:
                self.logger.error(f"Falha ao carregar o jogo: {save_name}")
                return False
            
            # Atualizar estado do jogo
            self.game_state = loaded_state
            
            # Inicializar controladores com o estado carregado
            self._initialize_controllers()
            
            # Emitir sinal para a GUI
            self.game_loaded.emit()
            self.logger.info(f"Jogo carregado com sucesso: {save_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar o jogo: {e}", exc_info=True)
            return False
    
    def save_game(self, save_name: str, is_autosave: bool = False) -> bool:
        """
        Salva o jogo atual.
        
        Args:
            save_name: Nome para o arquivo de salvamento
            is_autosave: Indica se é um autosave
            
        Returns:
            True se o salvamento foi bem-sucedido, False caso contrário
        """
        self.logger.info(f"Salvando jogo como: {save_name}")
        
        try:
            # Preparar metadados adicionais
            metadata = {
                "is_autosave": is_autosave,
                "turn": self.game_state.current_turn,
                "player_civ": self.game_state.player_civ.id if self.game_state.player_civ else None
            }
            
            # Salvar estado do jogo para arquivo
            result = self.save_manager.save_game(self.game_state, save_name, metadata)
            
            if not result:
                self.logger.error(f"Falha ao salvar o jogo: {save_name}")
                return False
            
            # Emitir sinal para a GUI
            self.game_saved.emit()
            self.logger.info(f"Jogo salvo com sucesso: {save_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar o jogo: {e}", exc_info=True)
            return False
    
    def end_turn(self) -> None:
        """Finaliza o turno atual e processa os turnos da IA."""
        self.logger.info(f"Finalizando turno {self.game_state.current_turn}")
        
        # Delegar para o controlador de turnos
        self.turn_controller.end_turn()
        
        # Autosave a cada N turnos
        if self.autosave_enabled and self.game_state.current_turn % self.autosave_interval == 0:
            self.save_game('autosave', is_autosave=True)
        
        # Emitir sinal para a GUI
        self.turn_changed.emit()
    
    def start_autosave(self):
        """
        Inicia o autosave em background, salvando a cada N turnos se habilitado.
        """
        if not self.autosave_enabled:
            self.logger.info("Autosave está desabilitado.")
            return
        def get_state():
            return self.game_state.to_dict() if self.game_state else None
        self.save_manager.autosave(get_state, interval_sec=self.autosave_interval * 2)  # Exemplo: 2s por turno
        self.logger.info(f"Autosave iniciado a cada {self.autosave_interval} turnos.")
    
    # Métodos de delegação para controladores especializados
    # Estes métodos implementam o padrão Facade, simplificando a interface
    
    def perform_unit_action(self, unit, action: Dict[str, Any]) -> Dict[str, Any]:
        """Delega ação de unidade para o controlador de unidades."""
        return self.unit_controller.perform_action(unit, action)
    
    def perform_city_action(self, city, action: Dict[str, Any]) -> Dict[str, Any]:
        """Delega ação de cidade para o controlador de cidades."""
        return self.city_controller.perform_action(city, action)
    
    def research_technology(self, tech_id: str) -> Dict[str, Any]:
        """Delega pesquisa de tecnologia para o controlador de tecnologias."""
        return self.tech_controller.start_research(self.game_state.player_civ, tech_id)
    
    def perform_diplomatic_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Delega ação diplomática para o controlador de civilizações."""
        return self.civ_controller.perform_diplomatic_action(action)
    
    def check_victory_conditions(self) -> Dict[str, Any]:
        """Delega verificação de condições de vitória para o controlador de civilizações."""
        return self.civ_controller.check_victory_conditions()
    
    # Métodos de acesso a dados
    # Estes métodos fornecem acesso simplificado aos dados do jogo
    
    def get_tech_tree(self) -> Dict[str, Any]:
        """Obtém a árvore tecnológica."""
        return self.data_loader.load_tech_tree()
    
    def get_building_data(self) -> Dict[str, Any]:
        """Obtém dados de edifícios."""
        return self.data_loader.load_buildings()
    
    def get_unit_data(self) -> Dict[str, Any]:
        """Obtém dados de unidades."""
        return self.data_loader.load_units()
    
    def get_world(self) -> Optional[World]:
        """Obtém o mundo do jogo."""
        return self.game_state.world if self.game_state else None
    
    def get_game_state(self) -> Optional[GameState]:
        """Obtém o estado atual do jogo."""
        return self.game_state
    
    def get_current_civilization(self):
        """Obtém a civilização atual do jogador."""
        return self.game_state.player_civ if self.game_state else None
    
    def get_all_units(self) -> List:
        """
        Obtém todas as unidades no jogo.
        
        Returns:
            Lista de todas as unidades.
        """
        if not self.game_state:
            return []
        
        all_units = []
        for civ in self.game_state.civilizations:
            all_units.extend(civ.units)
        
        return all_units
    
    def get_all_cities(self) -> List:
        """
        Obtém todas as cidades no jogo.
        
        Returns:
            Lista de todas as cidades.
        """
        if not self.game_state:
            return []
        
        all_cities = []
        for civ in self.game_state.civilizations:
            all_cities.extend(civ.cities)
        
        return all_cities
    
    def get_save_list(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de jogos salvos disponíveis.
        
        Returns:
            Lista de dicionários com informações sobre os salvamentos.
        """
        return self.save_manager.list_saves()
    
    def get_autosave_list(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de autosaves disponíveis.
        
        Returns:
            Lista de dicionários com informações sobre os autosaves.
        """
        return self.save_manager.list_autosaves()
    
    def delete_save(self, save_name: str) -> bool:
        """
        Exclui um jogo salvo.
        
        Args:
            save_name: Nome do arquivo de salvamento.
            
        Returns:
            True se a exclusão foi bem-sucedida, False caso contrário.
        """
        return self.save_manager.delete_save(save_name)
    
    def set_config_option(self, key: str, value: Any) -> bool:
        """
        Define uma opção de configuração.
        
        Args:
            key: Nome da opção.
            value: Valor da opção.
            
        Returns:
            True se a opção foi definida com sucesso, False caso contrário.
        """
        if key in self.config:
            self.config[key] = value
            return True
        return False
    
    def get_config_option(self, key: str, default: Any = None) -> Any:
        """
        Obtém uma opção de configuração.
        
        Args:
            key: Nome da opção.
            default: Valor padrão caso a opção não exista.
            
        Returns:
            Valor da opção ou o valor padrão.
        """
        return self.config.get(key, default)
    
    def restart_game(self) -> None:
        """Reinicia o jogo atual com as mesmas configurações."""
        if not self.game_state:
            self.logger.warning("Tentativa de reiniciar jogo sem um jogo ativo")
            return
        
        # Salvar configurações atuais
        current_config = {
            'world_size': self.game_state.config.get('world_size', 'standard'),
            'world_type': self.game_state.config.get('world_type', 'continents'),
            'num_civs': len(self.game_state.civilizations),
            'player_civ': self.game_state.player_civ.id if self.game_state.player_civ else 'rome'
        }
        
        # Iniciar novo jogo com as mesmas configurações
        self.new_game(current_config)
        self.logger.info("Jogo reiniciado com as mesmas configurações")
    
    def exit_game(self) -> None:
        """Prepara o jogo para ser encerrado, salvando configurações e estado se necessário."""
        self.logger.info("Preparando para encerrar o jogo")
        
        # Salvar configurações atuais
        self.data_loader.save_config(self.config)
        
        # Fazer autosave final se um jogo estiver em andamento
        if self.game_state and self.autosave_enabled:
            self.save_game("exit_save", is_autosave=True)
        
        self.logger.info("Jogo encerrado com sucesso")
