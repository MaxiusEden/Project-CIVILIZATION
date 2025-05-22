"""
Controlador responsável por gerenciar a pesquisa de tecnologias.
"""
import logging
from typing import Dict, Any, List, Optional

from game.models.civilization import Civilization
from game.utils.event_bus import EventBus

class TechController:
    """
    Gerencia a pesquisa de tecnologias, incluindo o progresso de pesquisa
    e a descoberta de novas tecnologias.
    """
    
    def __init__(self, game_controller, event_bus: Optional[EventBus] = None):
        """
        Inicializa o controlador de tecnologias.
        
        Args:
            game_controller: Referência ao controlador principal do jogo
            event_bus: Barramento de eventos para comunicação (opcional)
        """
        self.logger = logging.getLogger(__name__)
        self.game_controller = game_controller
        self.event_bus = event_bus or EventBus()
        
        # Carregar dados de tecnologias
        self.tech_data = self.game_controller.data_loader.get_tech_tree()
    
    def start_research(self, civ: Civilization, tech_id: str) -> Dict[str, Any]:
        """
        Inicia a pesquisa de uma tecnologia para uma civilização.
        
        Args:
            civ: Civilização que está pesquisando
            tech_id: ID da tecnologia a ser pesquisada
            
        Returns:
            Dicionário com o resultado da operação
        """
        self.logger.info(f"{civ.name} iniciando pesquisa de {tech_id}")
        
        # Verificar se a tecnologia existe
        if tech_id not in self.tech_data:
            self.logger.warning(f"Tecnologia não encontrada: {tech_id}")
            return {"success": False, "message": f"Tecnologia não encontrada: {tech_id}"}
        
        # Verificar se a civilização já possui a tecnologia
        if tech_id in civ.technologies:
            self.logger.warning(f"{civ.name} já possui a tecnologia {tech_id}")
            return {"success": False, "message": f"Você já possui esta tecnologia"}
        
        # Verificar pré-requisitos
        prerequisites = self.tech_data[tech_id].get("prerequisites", [])
        for prereq in prerequisites:
            if prereq not in civ.technologies:
                self.logger.warning(f"{civ.name} não possui pré-requisito {prereq} para {tech_id}")
                return {
                    "success": False, 
                    "message": f"Você precisa pesquisar {self.tech_data[prereq]['name']} primeiro"
                }
        
        # Definir a tecnologia atual
        civ.current_research = tech_id
        civ.research_progress = 0
        
        # Publicar evento de início de pesquisa
        self.event_bus.publish("tech.research_started", {
            "civ_id": civ.id,
            "tech_id": tech_id,
            "tech_name": self.tech_data[tech_id]["name"]
        })
        
        return {
            "success": True,
            "message": f"Iniciando pesquisa de {self.tech_data[tech_id]['name']}"
        }
    
    def process_research(self, civ: Civilization) -> None:
        """
        Processa o progresso de pesquisa para uma civilização.
        
        Args:
            civ: Civilização a ser processada
        """
        if not civ.current_research:
            return
        
        tech_id = civ.current_research
        
        # Verificar se a tecnologia existe
        if tech_id not in self.tech_data:
            self.logger.warning(f"Tecnologia inválida em pesquisa: {tech_id}")
            civ.current_research = None
            return
        
        # Calcular ciência produzida neste turno
        science_per_turn = self._calculate_science(civ)
        
        # Atualizar progresso
        civ.research_progress += science_per_turn
        
        # Verificar se a pesquisa foi concluída
        tech_cost = self.tech_data[tech_id]["cost"]
        if civ.research_progress >= tech_cost:
            self._complete_research(civ, tech_id)
    
    def _complete_research(self, civ: Civilization, tech_id: str) -> None:
        """
        Completa a pesquisa de uma tecnologia para uma civilização.
        
        Args:
            civ: Civilização que está pesquisando
            tech_id: ID da tecnologia pesquisada
        """
        self.logger.info(f"{civ.name} completou a pesquisa de {tech_id}")
        
        # Adicionar tecnologia à lista de tecnologias da civilização
        civ.technologies.append(tech_id)
        
        # Resetar pesquisa atual
        civ.current_research = None
        civ.research_progress = 0
        
        # Publicar evento de conclusão de pesquisa
        self.event_bus.publish("tech.research_completed", {
            "civ_id": civ.id,
            "tech_id": tech_id,
            "tech_name": self.tech_data[tech_id]["name"]
        })
        
        # Verificar tecnologias desbloqueadas
        self._check_unlocked_techs(civ)
    
    def _check_unlocked_techs(self, civ: Civilization) -> None:
        """
        Verifica quais tecnologias foram desbloqueadas para uma civilização.
        
        Args:
            civ: Civilização a ser verificada
        """
        unlocked_techs = []
        
        for tech_id, tech_data in self.tech_data.items():
            # Pular tecnologias já pesquisadas
            if tech_id in civ.technologies:
                continue
            
            # Verificar se todos os pré-requisitos foram atendidos
            prerequisites = tech_data.get("prerequisites", [])
            all_prereqs_met = True
            
            for prereq in prerequisites:
                if prereq not in civ.technologies:
                    all_prereqs_met = False
                    break
            
            if all_prereqs_met:
                unlocked_techs.append(tech_id)
        
        # Publicar evento de tecnologias desbloqueadas
        if unlocked_techs:
            self.event_bus.publish("tech.unlocked", {
                "civ_id": civ.id,
                "techs": unlocked_techs
            })
    
    def _calculate_science(self, civ: Civilization) -> int:
        """
        Calcula a quantidade de ciência produzida por uma civilização em um turno.
        
        Args:
            civ: Civilização a ser calculada
            
        Returns:
            Quantidade de ciência produzida
        """
        # Base de ciência
        science = 0
        
        # Adicionar ciência das cidades
        for city in civ.cities:
            science += city.science_output
        
        # Aplicar modificadores
        science_modifier = 1.0
        
        # Modificador de dificuldade
        if civ == self.game_controller.game_state.player_civ:
            difficulty = self.game_controller.config.get("difficulty", "prince")
            difficulty_data = self.game_controller.data_loader.get_difficulty_data(difficulty)
            science_modifier *= difficulty_data.get("player_science_modifier", 1.0)
        else:
            difficulty = self.game_controller.config.get("difficulty", "prince")
            difficulty_data = self.game_controller.data_loader.get_difficulty_data(difficulty)
            science_modifier *= difficulty_data.get("ai_science_modifier", 1.0)
        
        # Modificador de velocidade do jogo
        game_speed = self.game_controller.config.get("game_speed", "standard")
        speed_data = self.game_controller.data_loader.get_game_speed_data(game_speed)
        science_modifier *= speed_data.get("research_speed", 1.0)
        
        # Aplicar modificador
        science = int(science * science_modifier)
        
        return max(1, science)  # Garantir pelo menos 1 de ciência por turno
    
    def get_research_progress(self, civ: Civilization) -> Dict[str, Any]:
        """
        Obtém informações sobre o progresso de pesquisa de uma civilização.
        
        Args:
            civ: Civilização a ser verificada
            
        Returns:
            Dicionário com informações sobre o progresso de pesquisa
        """
        if not civ.current_research:
            return {
                "researching": False,
                "tech_id": None,
                "tech_name": None,
                "progress": 0,
                "total": 0,
                "turns_remaining": 0
            }
        
        tech_id = civ.current_research
        tech_data = self.tech_data.get(tech_id, {})
        tech_cost = tech_data.get("cost", 0)
        science_per_turn = self._calculate_science(civ)
        
        # Calcular turnos restantes
        remaining_science = tech_cost - civ.research_progress
        turns_remaining = (remaining_science + science_per_turn - 1) // science_per_turn  # Arredondamento para cima
        
        return {
            "researching": True,
            "tech_id": tech_id,
            "tech_name": tech_data.get("name", tech_id),
            "progress": civ.research_progress,
            "total": tech_cost,
            "turns_remaining": turns_remaining,
            "science_per_turn": science_per_turn
        }
    
    def get_available_techs(self, civ: Civilization) -> List[Dict[str, Any]]:
        """
        Obtém a lista de tecnologias disponíveis para pesquisa por uma civilização.
        
        Args:
            civ: Civilização a ser verificada
            
        Returns:
            Lista de dicionários com informações sobre as tecnologias disponíveis
        """
        available_techs = []
        
        for tech_id, tech_data in self.tech_data.items():
            # Pular tecnologias já pesquisadas
            if tech_id in civ.technologies:
                continue
            
            # Verificar se todos os pré-requisitos foram atendidos
            prerequisites = tech_data.get("prerequisites", [])
            all_prereqs_met = True
            
            for prereq in prerequisites:
                if prereq not in civ.technologies:
                    all_prereqs_met = False
                    break
            
            if all_prereqs_met:
                available_techs.append({
                    "id": tech_id,
                    "name": tech_data.get("name", tech_id),
                    "cost": tech_data.get("cost", 0),
                    "description": tech_data.get("description", ""),
                    "era": tech_data.get("era", "ancient"),
                    "unlocks": tech_data.get("unlocks", [])
                })
        
        return available_techs
