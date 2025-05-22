"""
Controlador responsável por gerenciar a lógica de turnos do jogo.
"""
import logging
from typing import Dict, Any, List, Optional

from game.models.civilization import Civilization
from game.utils.event_bus import EventBus

class TurnController:
    """
    Gerencia a lógica de turnos, incluindo o processamento de início e fim de turno
    para todas as civilizações.
    """
    
    def __init__(self, game_controller, event_bus: Optional[EventBus] = None):
        """
        Inicializa o controlador de turnos.
        
        Args:
            game_controller: Referência ao controlador principal do jogo
            event_bus: Barramento de eventos para comunicação (opcional)
        """
        self.logger = logging.getLogger(__name__)
        self.game_controller = game_controller
        self.event_bus = event_bus or EventBus()
        
        # Registrar para eventos relevantes
        if event_bus:
            self.event_bus.subscribe("unit.moved", self._check_unit_turn_complete)
            self.event_bus.subscribe("city.production_complete", self._on_production_complete)
    
    def end_turn(self) -> None:
        """
        Finaliza o turno atual e processa os turnos da IA.
        """
        self.logger.info(f"Finalizando turno {self.game_state.current_turn}")
        
        # Processar fim de turno para civilização do jogador
        self.process_end_of_turn(self.game_state.player_civ)
        
        # Processar turnos da IA
        for civ in self.game_state.civilizations:
            if civ != self.game_state.player_civ:
                self.process_ai_turn(civ)
        
        # Incrementar contador de turnos
        self.game_state.current_turn += 1
        
        # Processar início de turno para todas as civilizações
        for civ in self.game_state.civilizations:
            self.process_start_of_turn(civ)
        
        # Publicar evento de fim de turno
        self.event_bus.publish("turn.ended", {
            "turn": self.game_state.current_turn,
            "player_civ": self.game_state.player_civ.id if self.game_state.player_civ else None
        })
    
    def process_end_of_turn(self, civ: Civilization) -> None:
        """
        Processa o fim de turno para uma civilização.
        
        Args:
            civ: Civilização a ser processada
        """
        self.logger.debug(f"Processando fim de turno para {civ.name}")
        
        # Processar cidades
        for city in civ.cities:
            self.game_controller.city_controller.process_end_of_turn(city)
        
        # Processar unidades
        for unit in civ.units:
            self.game_controller.unit_controller.process_end_of_turn(unit)
        
        # Processar pesquisa
        self.game_controller.tech_controller.process_research(civ)
        
        # Publicar evento de fim de turno para civilização
        self.event_bus.publish("turn.civ_end", {
            "civ_id": civ.id,
            "turn": self.game_state.current_turn
        })
    
    def process_start_of_turn(self, civ: Civilization) -> None:
        """
        Processa o início de turno para uma civilização.
        
        Args:
            civ: Civilização a ser processada
        """
        self.logger.debug(f"Processando início de turno para {civ.name}")
        
        # Resetar pontos de movimento para unidades
        for unit in civ.units:
            self.game_controller.unit_controller.reset_movement(unit)
        
        # Processar produção de cidades
        for city in civ.cities:
            self.game_controller.city_controller.process_production(city)
        
        # Publicar evento de início de turno para civilização
        self.event_bus.publish("turn.civ_start", {
            "civ_id": civ.id,
            "turn": self.game_state.current_turn
        })
    
    def process_ai_turn(self, civ: Civilization) -> None:
        """
        Processa o turno para uma civilização controlada pela IA.
        
        Args:
            civ: Civilização da IA a ser processada
        """
        self.logger.debug(f"Processando turno da IA para {civ.name}")
        
        # Processar fim de turno
        self.process_end_of_turn(civ)
        
        # Tomada de decisão da IA
        self.game_controller.civ_controller.process_ai_turn(civ)
        
        # Processar início de turno
        self.process_start_of_turn(civ)
    
    def _check_unit_turn_complete(self, data: Dict[str, Any]) -> None:
        """
        Verifica se todas as unidades do jogador completaram seus movimentos.
        
        Args:
            data: Dados do evento
        """
        # Implementação para verificar se todas as unidades do jogador completaram seus movimentos
        pass
    
    def _on_production_complete(self, data: Dict[str, Any]) -> None:
        """
        Manipulador para evento de conclusão de produção.
        
        Args:
            data: Dados do evento
        """
        # Implementação para lidar com a conclusão de produção
        pass
    
    @property
    def game_state(self):
        """Acesso ao estado do jogo."""
        return self.game_controller.game_state
