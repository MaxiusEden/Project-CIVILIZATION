"""
Controlador responsável por gerenciar eventos do jogo.
"""
import logging
import random
from typing import Dict, Any, List, Optional

from game.utils.event_bus import EventBus

class EventController:
    """
    Gerencia eventos do jogo, como eventos aleatórios, notificações e condições especiais.
    """
    
    def __init__(self, game_controller, event_bus: Optional[EventBus] = None):
        """
        Inicializa o controlador de eventos.
        
        Args:
            game_controller: Referência ao controlador principal do jogo
            event_bus: Barramento de eventos para comunicação (opcional)
        """
        self.logger = logging.getLogger(__name__)
        self.game_controller = game_controller
        self.event_bus = event_bus or EventBus()
        
        # Registrar para eventos relevantes
        if event_bus:
            self.event_bus.subscribe("turn.ended", self._on_turn_ended)
            self.event_bus.subscribe("tech.research_completed", self._on_tech_completed)
            self.event_bus.subscribe("city.founded", self._on_city_founded)
            self.event_bus.subscribe("unit.killed", self._on_unit_killed)
        
        # Carregar dados de eventos
        self.event_data = self.game_controller.data_loader.get_event_data()
        
        # Inicializar lista de eventos pendentes
        self.pending_events = []
    
    def setup_initial_events(self) -> None:
        """Configura eventos iniciais para o jogo."""
        self.logger.info("Configurando eventos iniciais")
        
        # Limpar eventos pendentes
        self.pending_events = []
        
        # Adicionar evento de boas-vindas
        self._add_notification_event("welcome", {
            "civ_name": self.game_controller.game_state.player_civ.name
        })
        
        # Adicionar evento de tutorial se for o primeiro jogo
        if self.game_controller.config.get("show_tutorial", True):
            self._add_notification_event("tutorial", {})
    
    def process_pending_events(self) -> List[Dict[str, Any]]:
        """
        Processa e retorna eventos pendentes.
        
        Returns:
            Lista de eventos pendentes
        """
        events = self.pending_events.copy()
        self.pending_events = []
        return events
    
    def _add_notification_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Adiciona um evento de notificação à lista de eventos pendentes.
        
        Args:
            event_type: Tipo de evento
            data: Dados do evento
        """
        # Obter texto da notificação
        notification_text = self._get_notification_text(event_type, data)
        
        # Adicionar evento à lista de pendentes
        self.pending_events.append({
            "type": "notification",
            "subtype": event_type,
            "text": notification_text,
            "data": data,
            "turn": self.game_controller.game_state.current_turn
        })
        
        # Publicar evento de notificação
        self.event_bus.publish("notification.added", {
            "type": event_type,
            "text": notification_text,
            "data": data
        })
    
    def _get_notification_text(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Obtém o texto de uma notificação com base no tipo e dados.
        
        Args:
            event_type: Tipo de evento
            data: Dados do evento
            
        Returns:
            Texto formatado da notificação
        """
        # Carregar textos de notificação
        game_text = self.game_controller.data_loader.get_game_text()
        notifications = game_text.get("notifications", {})
        
        # Obter template de texto
        template = notifications.get(event_type, f"Evento: {event_type}")
        
        # Formatar texto com dados
        try:
            return template.format(**data)
        except KeyError as e:
            self.logger.warning(f"Faltando dados para formatar notificação: {e}")
            return template
    
    def _on_turn_ended(self, data: Dict[str, Any]) -> None:
        """
        Manipulador para evento de fim de turno.
        
        Args:
            data: Dados do evento
        """
        turn = data.get("turn", 0)
        
        # Verificar eventos aleatórios baseados no turno
        self._check_random_events(turn)
        
        # Verificar eventos específicos do turno
        self._check_turn_specific_events(turn)
    
    def _on_tech_completed(self, data: Dict[str, Any]) -> None:
        """
        Manipulador para evento de conclusão de pesquisa.
        
        Args:
            data: Dados do evento
        """
        civ_id = data.get("civ_id")
        tech_id = data.get("tech_id")
        tech_name = data.get("tech_name")
        
        # Verificar se é a civilização do jogador
        if civ_id == self.game_controller.game_state.player_civ.id:
            # Adicionar notificação
            self._add_notification_event("tech_discovered", {
                "tech_name": tech_name
            })
            
            # Verificar eventos especiais relacionados à tecnologia
            self._check_tech_events(tech_id)
    
    def _on_city_founded(self, data: Dict[str, Any]) -> None:
        """
        Manipulador para evento de fundação de cidade.
        
        Args:
            data: Dados do evento
        """
        civ_id = data.get("civ_id")
        city_name = data.get("city_name")
        
        # Verificar se é a civilização do jogador
        if civ_id == self.game_controller.game_state.player_civ.id:
            # Adicionar notificação
            self._add_notification_event("city_founded", {
                "city_name": city_name
            })
    
    def _on_unit_killed(self, data: Dict[str, Any]) -> None:
        """
        Manipulador para evento de unidade morta.
        
        Args:
            data: Dados do evento
        """
        civ_id = data.get("civ_id")
        unit_name = data.get("unit_name")
        
        # Verificar se é a civilização do jogador
        if civ_id == self.game_controller.game_state.player_civ.id:
            # Adicionar notificação
            self._add_notification_event("unit_killed", {
                "unit_name": unit_name
            })
    
    def _check_random_events(self, turn: int) -> None:
        """
        Verifica e gera eventos aleatórios baseados no turno.
        
        Args:
            turn: Número do turno atual
        """
        # Probabilidade base de evento aleatório (ajustar conforme necessário)
        base_probability = 0.05  # 5% de chance por turno
        
        # Ajustar probabilidade com base na dificuldade
        difficulty = self.game_controller.config.get("difficulty", "prince")
        difficulty_data = self.game_controller.data_loader.get_difficulty_data(difficulty)
        event_modifier = difficulty_data.get("random_event_modifier", 1.0)
        
        probability = base_probability * event_modifier
        
        # Verificar se um evento aleatório deve ocorrer
        if random.random() < probability:
            # Selecionar um evento aleatório
            self._trigger_random_event()
    
    def _check_turn_specific_events(self, turn: int) -> None:
        """
        Verifica e gera eventos específicos para o turno atual.
        
        Args:
            turn: Número do turno atual
        """
        # Verificar eventos específicos do turno nos dados de eventos
        turn_events = self.event_data.get("turn_events", {})
        
        if str(turn) in turn_events:
            events = turn_events[str(turn)]
            for event in events:
                self._trigger_specific_event(event)
    
    def _check_tech_events(self, tech_id: str) -> None:
        """
        Verifica e gera eventos relacionados a uma tecnologia.
        
        Args:
            tech_id: ID da tecnologia
        """
        # Verificar eventos específicos da tecnologia nos dados de eventos
        tech_events = self.event_data.get("tech_events", {})
        
        if tech_id in tech_events:
            events = tech_events[tech_id]
            for event in events:
                self._trigger_specific_event(event)
    
    def _trigger_random_event(self) -> None:
        """Seleciona e dispara um evento aleatório."""
        # Obter lista de eventos aleatórios possíveis
        random_events = self.event_data.get("random_events", [])
        
        if not random_events:
            return
        
        # Selecionar um evento aleatório
        event = random.choice(random_events)
        
        # Verificar condições do evento
        if self._check_event_conditions(event):
            # Aplicar efeitos do evento
            self._apply_event_effects(event)
            
            # Adicionar notificação
            self._add_notification_event(event.get("notification_type", "random_event"), event.get("data", {}))
    
    def _trigger_specific_event(self, event: Dict[str, Any]) -> None:
        """
        Dispara um evento específico.
        
        Args:
            event: Dados do evento a ser disparado
        """
        # Verificar condições do evento
        if self._check_event_conditions(event):
            # Aplicar efeitos do evento
            self._apply_event_effects(event)
            
            # Adicionar notificação
            self._add_notification_event(event.get("notification_type", "specific_event"), event.get("data", {}))
    
    def _check_event_conditions(self, event: Dict[str, Any]) -> bool:
        """
        Verifica se as condições para um evento são atendidas.
        
        Args:
            event: Dados do evento
            
        Returns:
            True se as condições são atendidas, False caso contrário
        """
        conditions = event.get("conditions", {})
        
        # Se não houver condições, o evento sempre ocorre
        if not conditions:
            return True
        
        # Verificar condições de tecnologia
        required_techs = conditions.get("required_techs", [])
        for tech in required_techs:
            if tech not in self.game_controller.game_state.player_civ.technologies:
                return False
        
        # Verificar condições de recurso
        required_resources = conditions.get("required_resources", [])
        for resource in required_resources:
            if resource not in self.game_controller.game_state.player_civ.resources:
                return False
        
        # Verificar condições de população
        min_population = conditions.get("min_population", 0)
        total_population = sum(city.population for city in self.game_controller.game_state.player_civ.cities)
        if total_population < min_population:
            return False
        
        # Verificar condições de turno
        min_turn = conditions.get("min_turn", 0)
        max_turn = conditions.get("max_turn", float('inf'))
        current_turn = self.game_controller.game_state.current_turn
        if current_turn < min_turn or current_turn > max_turn:
            return False
        
        # Todas as condições foram atendidas
        return True
    
    def _apply_event_effects(self, event: Dict[str, Any]) -> None:
        """
        Aplica os efeitos de um evento.
        
        Args:
            event: Dados do evento
        """
        effects = event.get("effects", {})
        
        # Se não houver efeitos, não fazer nada
        if not effects:
            return
        
        # Aplicar efeitos de ouro
        gold_change = effects.get("gold", 0)
        if gold_change != 0:
            self.game_controller.game_state.player_civ.gold += gold_change
        
        # Aplicar efeitos de ciência
        science_change = effects.get("science", 0)
        if science_change != 0:
            self.game_controller.game_state.player_civ.research_progress += science_change
        
        # Aplicar efeitos de felicidade
        happiness_change = effects.get("happiness", 0)
        if happiness_change != 0:
            self.game_controller.game_state.player_civ.happiness += happiness_change
        
        # Aplicar efeitos de unidade
        spawn_units = effects.get("spawn_units", [])
        for unit_data in spawn_units:
            unit_type = unit_data.get("type")
            x = unit_data.get("x")
            y = unit_data.get("y")
            
            if unit_type and x is not None and y is not None:
                self.game_controller.unit_controller.create_unit(
                    self.game_controller.game_state.player_civ,
                    unit_type,
                    x,
                    y
                )
        
        # Aplicar efeitos de recurso
        add_resources = effects.get("add_resources", [])
        for resource in add_resources:
            if resource not in self.game_controller.game_state.player_civ.resources:
                self.game_controller.game_state.player_civ.resources.append(resource)
        
        # Publicar evento de efeitos aplicados
        self.event_bus.publish("event.effects_applied", {
            "event_type": event.get("type", "unknown"),
            "effects": effects
        })
