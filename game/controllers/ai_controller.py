"""
Controlador responsável por gerenciar a inteligência artificial do jogo.
"""
import logging
import random
from typing import Dict, Any, List, Optional, Tuple

from game.models.civilization import Civilization
from game.models.city import City
from game.models.unit import Unit
from game.utils.event_bus import EventBus

class AIController:
    """
    Gerencia a inteligência artificial do jogo, controlando as decisões
    das civilizações não controladas pelo jogador.
    """
    
    def __init__(self, game_controller, event_bus: Optional[EventBus] = None):
        """
        Inicializa o controlador de IA.
        
        Args:
            game_controller: Referência ao controlador principal do jogo
            event_bus: Barramento de eventos para comunicação (opcional)
        """
        self.logger = logging.getLogger(__name__)
        self.game_controller = game_controller
        self.event_bus = event_bus or EventBus()
        
        # Registrar para eventos relevantes
        if event_bus:
            self.event_bus.subscribe("turn.civ_start", self._on_civ_turn_start)
    
    def process_ai_turn(self, civ: Civilization) -> None:
        """
        Processa o turno para uma civilização controlada pela IA.
        
        Args:
            civ: Civilização da IA a ser processada
        """
        self.logger.debug(f"Processando IA para {civ.name}")
        
        # Definir prioridades para este turno
        priorities = self._determine_priorities(civ)
        
        # Processar pesquisa
        self._handle_research(civ, priorities)
        
        # Processar cidades
        for city in civ.cities:
            self._handle_city(civ, city, priorities)
        
        # Processar unidades
        for unit in civ.units:
            self._handle_unit(civ, unit, priorities)
        
        # Processar diplomacia
        self._handle_diplomacy(civ, priorities)
        
        # Publicar evento de turno da IA concluído
        self.event_bus.publish("ai.turn_completed", {
            "civ_id": civ.id,
            "turn": self.game_controller.game_state.current_turn
        })
    
    def _determine_priorities(self, civ: Civilization) -> Dict[str, float]:
        """
        Determina as prioridades da IA para este turno.
        
        Args:
            civ: Civilização da IA
            
        Returns:
            Dicionário com prioridades para diferentes aspectos do jogo
        """
        # Valores padrão
        priorities = {
            "expansion": 0.5,    # Prioridade para expansão territorial
            "military": 0.5,     # Prioridade para unidades militares
            "economy": 0.5,      # Prioridade para economia
            "science": 0.5,      # Prioridade para pesquisa
            "defense": 0.5       # Prioridade para defesa
        }
        
        # Ajustar com base na personalidade da civilização
        personality = civ.personality or "balanced"
        
        if personality == "aggressive":
            priorities["military"] += 0.3
            priorities["expansion"] += 0.2
            priorities["economy"] -= 0.1
            priorities["science"] -= 0.1
        elif personality == "scientific":
            priorities["science"] += 0.3
            priorities["economy"] += 0.1
            priorities["military"] -= 0.1
        elif personality == "expansionist":
            priorities["expansion"] += 0.3
            priorities["economy"] += 0.1
            priorities["defense"] -= 0.1
        elif personality == "defensive":
            priorities["defense"] += 0.3
            priorities["economy"] += 0.1
            priorities["expansion"] -= 0.1
        
        # Ajustar com base na situação atual
        
        # Se estiver em guerra, aumentar prioridade militar e defesa
        if self._is_at_war(civ):
            priorities["military"] += 0.2
            priorities["defense"] += 0.2
            priorities["expansion"] -= 0.1
            priorities["science"] -= 0.1
        
        # Se estiver atrás em tecnologia, aumentar prioridade de ciência
        if self._is_behind_in_tech(civ):
            priorities["science"] += 0.2
            priorities["military"] -= 0.1
        
        # Se tiver poucas cidades, aumentar prioridade de expansão
        if len(civ.cities) < 3:
            priorities["expansion"] += 0.2
        
        # Se tiver economia fraca, aumentar prioridade econômica
        if civ.gold < 100:
            priorities["economy"] += 0.2
            priorities["military"] -= 0.1
        
        # Normalizar prioridades para que fiquem entre 0 e 1
        for key in priorities:
            priorities[key] = max(0.1, min(1.0, priorities[key]))
        
        return priorities
    
    def _handle_research(self, civ: Civilization, priorities: Dict[str, float]) -> None:
        """
        Gerencia a pesquisa para uma civilização da IA.
        
        Args:
            civ: Civilização da IA
            priorities: Prioridades da IA
        """
        # Se já estiver pesquisando algo, continuar
        if civ.current_research:
            return
        
        # Obter tecnologias disponíveis
        available_techs = self.game_controller.tech_controller.get_available_techs(civ)
        
        if not available_techs:
            return
        
        # Avaliar cada tecnologia
        tech_scores = []
        
        for tech in available_techs:
            score = self._evaluate_tech(tech, civ, priorities)
            tech_scores.append((tech["id"], score))
        
        # Ordenar por pontuação (maior primeiro)
        tech_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Escolher a melhor tecnologia (com um pouco de aleatoriedade)
        if random.random() < 0.8:  # 80% de chance de escolher a melhor
            best_tech = tech_scores[0][0]
        else:
            # Escolher aleatoriamente entre as 3 melhores (se houver tantas)
            top_n = min(3, len(tech_scores))
            best_tech = tech_scores[random.randint(0, top_n-1)][0]
        
        # Iniciar pesquisa
        self.game_controller.tech_controller.start_research(civ, best_tech)
    
    def _handle_city(self, civ: Civilization, city: City, priorities: Dict[str, float]) -> None:
        """
        Gerencia uma cidade para uma civilização da IA.
        
        Args:
            civ: Civilização da IA
            city: Cidade a ser gerenciada
            priorities: Prioridades da IA
        """
        # Decidir o que construir
        if not city.current_production:
            self._choose_production(civ, city, priorities)
        
        # Gerenciar trabalhadores
        self._manage_workers(civ, city, priorities)
        
        # Decidir se deve comprar algo
        self._consider_purchases(civ, city, priorities)
    
    def _handle_unit(self, civ: Civilization, unit: Unit, priorities: Dict[str, float]) -> None:
        """
        Gerencia uma unidade para uma civilização da IA.
        
        Args:
            civ: Civilização da IA
            unit: Unidade a ser gerenciada
            priorities: Prioridades da IA
        """
        # Se a unidade não tiver movimentos restantes, pular
        if unit.movement_points <= 0:
            return
        
        # Decidir ação com base no tipo de unidade
        if unit.type == "settler":
            self._handle_settler(civ, unit, priorities)
        elif unit.type == "worker":
            self._handle_worker(civ, unit, priorities)
        elif unit.is_military:
            self._handle_military_unit(civ, unit, priorities)
        else:
            # Unidades civis genéricas
            self._handle_civilian_unit(civ, unit, priorities)
    
    def _handle_diplomacy(self, civ: Civilization, priorities: Dict[str, float]) -> None:
        """
        Gerencia diplomacia para uma civilização da IA.
        
        Args:
            civ: Civilização da IA
            priorities: Prioridades da IA
        """
        # Obter outras civilizações
        other_civs = [c for c in self.game_controller.game_state.civilizations if c != civ]
        
        for other_civ in other_civs:
            # Avaliar relação atual
            relation = self._evaluate_relation(civ, other_civ)
            
            # Decidir ação diplomática
            if relation < -50:  # Relação muito ruim
                if not self._is_at_war_with(civ, other_civ) and priorities["military"] > 0.7:
                    # Considerar declarar guerra
                    if random.random() < 0.2:  # 20% de chance
                        self._declare_war(civ, other_civ)
            elif relation < 0:  # Relação ruim
                # Evitar contato
                pass
            elif relation < 50:  # Relação neutra
                # Considerar acordo comercial
                if random.random() < 0.3:  # 30% de chance
                    self._propose_trade(civ, other_civ)
            else:  # Relação boa
                # Considerar acordo de amizade
                if random.random() < 0.4:  # 40% de chance
                    self._propose_friendship(civ, other_civ)
    
    def _evaluate_tech(self, tech: Dict[str, Any], civ: Civilization, priorities: Dict[str, float]) -> float:
        """
        Avalia o valor de uma tecnologia para a IA.
        
        Args:
            tech: Dados da tecnologia
            civ: Civilização da IA
            priorities: Prioridades da IA
            
        Returns:
            Pontuação da tecnologia
        """
        score = 0.0
        
        # Pontuação base pelo custo (tecnologias mais baratas são preferidas)
        score += 100 / max(1, tech["cost"])
        
        # Avaliar o que a tecnologia desbloqueia
        unlocks = tech.get("unlocks", [])
        
        for unlock in unlocks:
            # Unidades militares
            if unlock.get("type") == "unit" and unlock.get("is_military", False):
                score += 20 * priorities["military"]
            
            # Edifícios econômicos
            elif unlock.get("type") == "building" and unlock.get("yields", {}).get("gold", 0) > 0:
                score += 15 * priorities["economy"]
            
            # Edifícios científicos
            elif unlock.get("type") == "building" and unlock.get("yields", {}).get("science", 0) > 0:
                score += 15 * priorities["science"]
            
            # Melhorias de terreno
            elif unlock.get("type") == "improvement":
                score += 10 * priorities["economy"]
            
            # Maravilhas
            elif unlock.get("type") == "wonder":
                score += 25  # Maravilhas são sempre valiosas
        
        # Ajustar com base na era
        era_multipliers = {
            "ancient": 1.2,      # Priorizar tecnologias antigas
            "classical": 1.1,
            "medieval": 1.0,
            "renaissance": 0.9,
            "industrial": 0.8,
            "modern": 0.7,
            "atomic": 0.6,
            "information": 0.5   # Menor prioridade para tecnologias avançadas
        }
        
        era = tech.get("era", "ancient")
        score *= era_multipliers.get(era, 1.0)
        
        # Adicionar um pouco de aleatoriedade
        score *= random.uniform(0.9, 1.1)
        
        return score
    
    def _choose_production(self, civ: Civilization, city: City, priorities: Dict[str, float]) -> None:
        """
        Escolhe o que uma cidade deve produzir.
        
        Args:
            civ: Civilização da IA
            city: Cidade a ser gerenciada
            priorities: Prioridades da IA
        """
        # Obter opções de produção disponíveis
        available_units = self.game_controller.city_controller.get_available_units(city)
        available_buildings = self.game_controller.city_controller.get_available_buildings(city)
        
        # Avaliar cada opção
        options = []
        
        # Avaliar unidades
        for unit in available_units:
            score = self._evaluate_unit_production(unit, civ, city, priorities)
            options.append(("unit", unit["id"], score))
        
        # Avaliar edifícios
        for building in available_buildings:
            score = self._evaluate_building_production(building, civ, city, priorities)
            options.append(("building", building["id"], score))
        
        # Se não houver opções, retornar
        if not options:
            return
        
        # Ordenar por pontuação (maior primeiro)
        options.sort(key=lambda x: x[2], reverse=True)
        
        # Escolher a melhor opção (com um pouco de aleatoriedade)
        if random.random() < 0.7:  # 70% de chance de escolher a melhor
            best_option = options[0]
        else:
            # Escolher aleatoriamente entre as 3 melhores (se houver tantas)
            top_n = min(3, len(options))
            best_option = options[random.randint(0, top_n-1)]
        
        # Iniciar produção
        production_type, production_id = best_option[0], best_option[1]
        
        if production_type == "unit":
            self.game_controller.city_controller.start_unit_production(city, production_id)
        else:  # building
            self.game_controller.city_controller.start_building_production(city, production_id)
    
    def _evaluate_unit_production(self, unit: Dict[str, Any], civ: Civilization, city: City, priorities: Dict[str, float]) -> float:
        """
        Avalia o valor de produzir uma unidade.
        
        Args:
            unit: Dados da unidade
            civ: Civilização da IA
            city: Cidade produtora
            priorities: Prioridades da IA
            
        Returns:
            Pontuação da unidade
        """
        score = 0.0
        
        # Pontuação base pelo custo (unidades mais baratas são preferidas)
        score += 50 / max(1, unit["cost"])
        
        # Avaliar com base no tipo de unidade
        if unit.get("type") == "settler":
            # Colonos são valiosos para expansão
            # Mas não produzir se a cidade for pequena
            if city.population > 3 and len(civ.cities) < 6:
                score += 100 * priorities["expansion"]
            else:
                score -= 50  # Penalidade para cidades pequenas
        
        elif unit.get("type") == "worker":
            # Trabalhadores são valiosos para economia
            # Mas não produzir muitos
            worker_count = sum(1 for u in civ.units if u.type == "worker")
            if worker_count < len(civ.cities) * 1.5:
                score += 80 * priorities["economy"]
            else:
                score -= 30  # Penalidade se já tiver muitos trabalhadores
        
        elif unit.get("is_military", False):
            # Unidades militares são valiosas para defesa e ataque
            military_count = sum(1 for u in civ.units if u.is_military)
            
            # Calcular força militar ideal com base no número de cidades
            ideal_military = len(civ.cities) * 3
            
            if military_count < ideal_military:
                score += 70 * max(priorities["military"], priorities["defense"])
            else:
                score += 30 * priorities["military"]  # Ainda valioso, mas menos
            
            # Bônus para unidades de longo alcance
            if unit.get("range", 0) > 1:
                score += 20
            
            # Bônus para unidades fortes
            score += unit.get("strength", 0) * 0.5
        
        # Adicionar um pouco de aleatoriedade
        score *= random.uniform(0.9, 1.1)
        
        return score
    
    def _evaluate_building_production(self, building: Dict[str, Any], civ: Civilization, city: City, priorities: Dict[str, float]) -> float:
        """
        Avalia o valor de produzir um edifício.
        
        Args:
            building: Dados do edifício
            civ: Civilização da IA
            city: Cidade produtora
            priorities: Prioridades da IA
            
        Returns:
            Pontuação do edifício
        """
        score = 0.0
        
        # Pontuação base pelo custo (edifícios mais baratos são preferidos)
        score += 50 / max(1, building["cost"])
        
        # Avaliar com base nos rendimentos do edifício
        yields = building.get("yields", {})
        
        # Rendimento de ouro
        gold_yield = yields.get("gold", 0)
        score += gold_yield * 10 * priorities["economy"]
        
        # Rendimento de ciência
        science_yield = yields.get("science", 0)
        score += science_yield * 12 * priorities["science"]
        
        # Rendimento de produção
        production_yield = yields.get("production", 0)
        score += production_yield * 8 * (priorities["military"] + priorities["expansion"]) / 2
        
        # Rendimento de comida
        food_yield = yields.get("food", 0)
        score += food_yield * 10 * priorities["expansion"]
        
        # Rendimento de cultura
        culture_yield = yields.get("culture", 0)
        score += culture_yield * 8
        
        # Bônus para edifícios defensivos
        if building.get("defense_bonus", 0) > 0:
            score += building["defense_bonus"] * 5 * priorities["defense"]
        
        # Bônus para maravilhas
        if building.get("is_wonder", False):
            score += 50  # Maravilhas são sempre valiosas
        
        # Adicionar um pouco de aleatoriedade
        score *= random.uniform(0.9, 1.1)
        
        return score
    
    def _manage_workers(self, civ: Civilization, city: City, priorities: Dict[str, float]) -> None:
        """
        Gerencia a alocação de trabalhadores em uma cidade.
        
        Args:
            civ: Civilização da IA
            city: Cidade a ser gerenciada
            priorities: Prioridades da IA
        """
        # Implementação simplificada - a IA usa a alocação automática
        self.game_controller.city_controller.optimize_workers(city, priorities)
    
    def _consider_purchases(self, civ: Civilization, city: City, priorities: Dict[str, float]) -> None:
        """
        Decide se deve comprar algo com ouro.
        
        Args:
            civ: Civilização da IA
            city: Cidade a ser gerenciada
            priorities: Prioridades da IA
        """
        # Só considerar compras se tiver ouro suficiente
        if civ.gold < 200:
            return
        
        # Chance de comprar algo baseada na quantidade de ouro
        purchase_chance = min(0.5, civ.gold / 1000)
        
        if random.random() > purchase_chance:
            return
        
        # Decidir entre comprar unidade, edifício ou terreno
        options = ["unit", "building", "tile"]
        weights = [
            priorities["military"] + priorities["defense"],  # unidade
            priorities["economy"] + priorities["science"],   # edifício
            priorities["expansion"]                          # terreno
        ]
        
        # Normalizar pesos
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Escolher opção
        choice = random.choices(options, weights=weights, k=1)[0]
        
        if choice == "unit":
            self._consider_purchase_unit(civ, city, priorities)
        elif choice == "building":
            self._consider_purchase_building(civ, city, priorities)
        else:  # tile
            self._consider_purchase_tile(civ, city, priorities)
    
    def _consider_purchase_unit(self, civ: Civilization, city: City, priorities: Dict[str, float]) -> None:
        """
        Considera comprar uma unidade com ouro.
        
        Args:
            civ: Civilização da IA
            city: Cidade a ser gerenciada
            priorities: Prioridades da IA
        """
        # Obter unidades disponíveis para compra
        available_units = self.game_controller.city_controller.get_available_units(city)
        
        # Filtrar por custo
        affordable_units = [u for u in available_units if u["gold_cost"] <= civ.gold]
        
        if not affordable_units:
            return
        
        # Avaliar cada unidade
        unit_scores = []
        
        for unit in affordable_units:
            score = self._evaluate_unit_production(unit, civ, city, priorities)
            # Ajustar pontuação para compras (preferir unidades mais caras)
            score *= (unit["cost"] / 100) ** 0.5
            unit_scores.append((unit["id"], score))
        
        # Ordenar por pontuação
        unit_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Comprar a melhor unidade
        best_unit = unit_scores[0][0]
        self.game_controller.city_controller.purchase_unit(city, best_unit)
    
    def _consider_purchase_building(self, civ: Civilization, city: City, priorities: Dict[str, float]) -> None:
        """
        Considera comprar um edifício com ouro.
        
        Args:
            civ: Civilização da IA
            city: Cidade a ser gerenciada
            priorities: Prioridades da IA
        """
        # Obter edifícios disponíveis para compra
        available_buildings = self.game_controller.city_controller.get_available_buildings(city)
        
        # Filtrar por custo
        affordable_buildings = [b for b in available_buildings if b["gold_cost"] <= civ.gold]
        
        if not affordable_buildings:
            return
        
        # Avaliar cada edifício
        building_scores = []
        
        for building in affordable_buildings:
            score = self._evaluate_building_production(building, civ, city, priorities)
            # Ajustar pontuação para compras (preferir edifícios mais caros)
            score *= (building["cost"] / 100) ** 0.5
            building_scores.append((building["id"], score))
        
        # Ordenar por pontuação
        building_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Comprar o melhor edifício
        best_building = building_scores[0][0]
        self.game_controller.city_controller.purchase_building(city, best_building)
    
    def _consider_purchase_tile(self, civ: Civilization, city: City, priorities: Dict[str, float]) -> None:
        """
        Considera comprar um terreno com ouro.
        
        Args:
            civ: Civilização da IA
            city: Cidade a ser gerenciada
            priorities: Prioridades da IA
        """
        # Obter terrenos disponíveis para compra
        available_tiles = self.game_controller.city_controller.get_available_tiles(city)
        
        # Filtrar por custo
        affordable_tiles = [t for t in available_tiles if t["gold_cost"] <= civ.gold]
        
        if not affordable_tiles:
            return
        
        # Avaliar cada terreno
        tile_scores = []
        
        for tile in affordable_tiles:
            score = self._evaluate_tile(tile, civ, city, priorities)
            tile_scores.append((tile["x"], tile["y"], score))
        
        # Ordenar por pontuação
        tile_scores.sort(key=lambda x: x[2], reverse=True)
        
        # Comprar o melhor terreno
        best_tile_x, best_tile_y = tile_scores[0][0], tile_scores[0][1]
        self.game_controller.city_controller.purchase_tile(city, best_tile_x, best_tile_y)
    
    def _evaluate_tile(self, tile: Dict[str, Any], civ: Civilization, city: City, priorities: Dict[str, float]) -> float:
        """
        Avalia o valor de um terreno.
        
        Args:
            tile: Dados do terreno
            civ: Civilização da IA
            city: Cidade relacionada
            priorities: Prioridades da IA
            
        Returns:
            Pontuação do terreno
        """
        score = 0.0
        
        # Avaliar com base nos rendimentos do terreno
        yields = tile.get("yields", {})
        
        # Rendimento de comida
        food_yield = yields.get("food", 0)
        score += food_yield * 10 * priorities["expansion"]
        
        # Rendimento de produção
        production_yield = yields.get("production", 0)
        score += production_yield * 8 * (priorities["military"] + priorities["economy"]) / 2
        
        # Rendimento de ouro
        gold_yield = yields.get("gold", 0)
        score += gold_yield * 10 * priorities["economy"]
        
        # Bônus para terrenos com recursos
        if tile.get("resource"):
            score += 30
            
            # Bônus adicional para recursos estratégicos
            if tile.get("resource_type") == "strategic":
                score += 20 * priorities["military"]
            
            # Bônus adicional para recursos de luxo
            elif tile.get("resource_type") == "luxury":
                score += 15 * priorities["economy"]
        
        # Bônus para terrenos adjacentes a outras cidades ou unidades inimigas
        if tile.get("is_border", False):
            score += 10 * priorities["defense"]
        
        # Penalidade para terrenos distantes do centro da cidade
        distance = tile.get("distance", 1)
        score -= distance * 5
        
        # Adicionar um pouco de aleatoriedade
        score *= random.uniform(0.9, 1.1)
        
        return score
    
    def _handle_settler(self, civ: Civilization, unit: Unit, priorities: Dict[str, float]) -> None:
        """
        Gerencia um colono para uma civilização da IA.
        
        Args:
            civ: Civilização da IA
            unit: Unidade colono
            priorities: Prioridades da IA
        """
        # Verificar se deve fundar uma cidade na posição atual
        if self._is_good_city_location(unit.x, unit.y, civ):
            self.game_controller.unit_controller.found_city(unit)
            return
        
        # Buscar um bom local para cidade
        target = self._find_city_location(civ, unit, priorities)
        
        if target:
            # Mover em direção ao alvo
            path = self.game_controller.world_controller.find_path(unit.x, unit.y, target[0], target[1])
            
            if path and len(path) > 1:
                next_pos = path[1]  # O primeiro ponto é a posição atual
                self.game_controller.unit_controller.move_unit(unit, next_pos[0], next_pos[1])
        else:
            # Mover aleatoriamente se não encontrar um bom local
            self._move_randomly(unit)
    
    def _handle_worker(self, civ: Civilization, unit: Unit, priorities: Dict[str, float]) -> None:
        """
        Gerencia um trabalhador para uma civilização da IA.
        
        Args:
            civ: Civilização da IA
            unit: Unidade trabalhador
            priorities: Prioridades da IA
        """
        # Verificar se há melhorias para construir no tile atual
        current_tile = self.game_controller.world_controller.get_tile(unit.x, unit.y)
        
        if current_tile and self._should_build_improvement(current_tile, civ, priorities):
            improvement = self._choose_improvement(current_tile, civ, priorities)
            if improvement:
                self.game_controller.unit_controller.build_improvement(unit, improvement)
                return
        
        # Buscar um tile para melhorar
        target = self._find_tile_to_improve(civ, unit, priorities)
        
        if target:
            # Mover em direção ao alvo
            path = self.game_controller.world_controller.find_path(unit.x, unit.y, target[0], target[1])
            
            if path and len(path) > 1:
                next_pos = path[1]  # O primeiro ponto é a posição atual
                self.game_controller.unit_controller.move_unit(unit, next_pos[0], next_pos[1])
        else:
            # Mover para perto de uma cidade se não encontrar um tile para melhorar
            nearest_city = self._find_nearest_city(civ, unit.x, unit.y)
            
            if nearest_city:
                path = self.game_controller.world_controller.find_path(
                    unit.x, unit.y, nearest_city.x, nearest_city.y
                )
                
                if path and len(path) > 1:
                    next_pos = path[1]
                    self.game_controller.unit_controller.move_unit(unit, next_pos[0], next_pos[1])
            else:
                # Mover aleatoriamente se não encontrar uma cidade
                self._move_randomly(unit)
    
    def _handle_military_unit(self, civ: Civilization, unit: Unit, priorities: Dict[str, float]) -> None:
        """
        Gerencia uma unidade militar para uma civilização da IA.
        
        Args:
            civ: Civilização da IA
            unit: Unidade militar
            priorities: Prioridades da IA
        """
        # Verificar se há inimigos próximos para atacar
        enemy = self._find_nearest_enemy(civ, unit.x, unit.y, unit.range)
        
        if enemy and self._should_attack(unit, enemy, priorities):
            # Atacar inimigo
            self.game_controller.unit_controller.attack(unit, enemy.x, enemy.y)
            return
        
        # Verificar se está em guerra e deve se mover para o front
        if self._is_at_war(civ) and priorities["military"] > 0.6:
            target = self._find_military_target(civ, unit, priorities)
            
            if target:
                # Mover em direção ao alvo
                path = self.game_controller.world_controller.find_path(unit.x, unit.y, target[0], target[1])
                
                if path and len(path) > 1:
                    next_pos = path[1]
                    self.game_controller.unit_controller.move_unit(unit, next_pos[0], next_pos[1])
                return
        
        # Se não estiver em guerra ou não tiver alvo, mover para posição estratégica
        if priorities["defense"] > priorities["military"]:
            # Modo defensivo: mover para perto de cidades
            nearest_city = self._find_nearest_city(civ, unit.x, unit.y)
            
            if nearest_city and self._distance(unit.x, unit.y, nearest_city.x, nearest_city.y) > 2:
                path = self.game_controller.world_controller.find_path(
                    unit.x, unit.y, nearest_city.x, nearest_city.y
                )
                
                if path and len(path) > 1:
                    next_pos = path[1]
                    self.game_controller.unit_controller.move_unit(unit, next_pos[0], next_pos[1])
                return
        else:
            # Modo ofensivo: mover para fronteiras
            border = self._find_border_position(civ, unit)
            
            if border:
                path = self.game_controller.world_controller.find_path(unit.x, unit.y, border[0], border[1])
                
                if path and len(path) > 1:
                    next_pos = path[1]
                    self.game_controller.unit_controller.move_unit(unit, next_pos[0], next_pos[1])
                return
        
        # Se não tiver nada melhor para fazer, mover aleatoriamente
        self._move_randomly(unit)
    
    def _handle_civilian_unit(self, civ: Civilization, unit: Unit, priorities: Dict[str, float]) -> None:
        """
        Gerencia uma unidade civil genérica para uma civilização da IA.
        
        Args:
            civ: Civilização da IA
            unit: Unidade civil
            priorities: Prioridades da IA
        """
        # Mover para a cidade mais próxima
        nearest_city = self._find_nearest_city(civ, unit.x, unit.y)
        
        if nearest_city:
            path = self.game_controller.world_controller.find_path(
                unit.x, unit.y, nearest_city.x, nearest_city.y
            )
            
            if path and len(path) > 1:
                next_pos = path[1]
                self.game_controller.unit_controller.move_unit(unit, next_pos[0], next_pos[1])
        else:
            # Mover aleatoriamente se não encontrar uma cidade
            self._move_randomly(unit)
    
    def _move_randomly(self, unit: Unit) -> None:
        """
        Move uma unidade em uma direção aleatória válida.
        
        Args:
            unit: Unidade a ser movida
        """
        # Obter movimentos possíveis
        possible_moves = self.game_controller.world_controller.get_valid_moves(unit)
        
        if possible_moves:
            # Escolher um movimento aleatório
            move = random.choice(possible_moves)
            self.game_controller.unit_controller.move_unit(unit, move[0], move[1])
    
    def _is_at_war(self, civ: Civilization) -> bool:
        """
        Verifica se uma civilização está em guerra.
        
        Args:
            civ: Civilização a ser verificada
            
        Returns:
            True se a civilização estiver em guerra, False caso contrário
        """
        for other_civ in self.game_controller.game_state.civilizations:
            if other_civ != civ and self._is_at_war_with(civ, other_civ):
                return True
        return False
    
    def _is_at_war_with(self, civ1: Civilization, civ2: Civilization) -> bool:
        """
        Verifica se duas civilizações estão em guerra.
        
        Args:
            civ1: Primeira civilização
            civ2: Segunda civilização
            
        Returns:
            True se as civilizações estiverem em guerra, False caso contrário
        """
        return civ2.id in civ1.at_war_with
    
    def _is_behind_in_tech(self, civ: Civilization) -> bool:
        """
        Verifica se uma civilização está atrás em tecnologia.
        
        Args:
            civ: Civilização a ser verificada
            
        Returns:
            True se a civilização estiver atrás em tecnologia, False caso contrário
        """
        # Contar tecnologias de cada civilização
        tech_counts = {}
        
        for c in self.game_controller.game_state.civilizations:
            tech_counts[c.id] = len(c.technologies)
        
        # Calcular média
        avg_techs = sum(tech_counts.values()) / len(tech_counts)
        
        # Verificar se está abaixo da média
        return tech_counts[civ.id] < avg_techs * 0.9  # 10% abaixo da média
    
    def _evaluate_relation(self, civ1: Civilization, civ2: Civilization) -> int:
        """
        Avalia a relação entre duas civilizações.
        
        Args:
            civ1: Primeira civilização
            civ2: Segunda civilização
            
        Returns:
            Valor da relação (negativo para ruim, positivo para bom)
        """
        # Valor base
        relation = 0
        
        # Se estiver em guerra, relação muito ruim
        if self._is_at_war_with(civ1, civ2):
            relation -= 100
        
        # Verificar acordos
        if civ2.id in civ1.trade_agreements:
            relation += 20
        
        if civ2.id in civ1.friendships:
            relation += 50
        
        if civ2.id in civ1.denounced:
            relation -= 50
        
        # Verificar histórico de guerra
        if civ2.id in civ1.war_history:
            relation -= 30
        
        # Verificar proximidade de fronteiras
        if self._has_border_with(civ1, civ2):
            # Civilizações expansionistas não gostam de fronteiras próximas
            if civ1.personality == "expansionist":
                relation -= 20
            else:
                relation += 10
        
        # Verificar diferença de força militar
        military_diff = self._get_military_strength(civ1) - self._get_military_strength(civ2)
        if military_diff > 0:
            # Civilizações mais fortes tendem a ser mais agressivas
            relation -= min(30, military_diff // 10)
        else:
            # Civilizações mais fracas tendem a ser mais cautelosas
            relation += min(20, abs(military_diff) // 10)
        
        return relation
    
    def _get_military_strength(self, civ: Civilization) -> int:
        """
        Calcula a força militar de uma civilização.
        
        Args:
            civ: Civilização a ser avaliada
            
        Returns:
            Valor da força militar
        """
        strength = 0
        
        for unit in civ.units:
            if unit.is_military:
                strength += unit.strength
        
        return strength
    
    def _has_border_with(self, civ1: Civilization, civ2: Civilization) -> bool:
        """
        Verifica se duas civilizações compartilham fronteiras.
        
        Args:
            civ1: Primeira civilização
            civ2: Segunda civilização
            
        Returns:
            True se as civilizações compartilharem fronteiras, False caso contrário
        """
        # Implementação simplificada - verificar se há tiles adjacentes
        world = self.game_controller.game_state.world
        
        # Obter todos os tiles de cada civilização
        civ1_tiles = []
        civ2_tiles = []
        
        for x in range(world.width):
            for y in range(world.height):
                tile = world.get_tile(x, y)
                if not tile:
                    continue
                
                if tile.owner == civ1.id:
                    civ1_tiles.append((x, y))
                elif tile.owner == civ2.id:
                    civ2_tiles.append((x, y))
        
        # Verificar se há tiles adjacentes
        for x1, y1 in civ1_tiles:
            for x2, y2 in civ2_tiles:
                if self._is_adjacent(x1, y1, x2, y2):
                    return True
        
        return False
    
    def _is_adjacent(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Verifica se duas posições são adjacentes.
        
        Args:
            x1, y1: Coordenadas da primeira posição
            x2, y2: Coordenadas da segunda posição
            
        Returns:
            True se as posições forem adjacentes, False caso contrário
        """
        # Para grade hexagonal
        if y1 % 2 == 0:  # Linha par
            adjacents = [
                (x1, y1-1), (x1+1, y1-1),
                (x1-1, y1), (x1+1, y1),
                (x1, y1+1), (x1+1, y1+1)
            ]
        else:  # Linha ímpar
            adjacents = [
                (x1-1, y1-1), (x1, y1-1),
                (x1-1, y1), (x1+1, y1),
                (x1-1, y1+1), (x1, y1+1)
            ]
        
        return (x2, y2) in adjacents
    
    def _declare_war(self, civ1: Civilization, civ2: Civilization) -> None:
        """
        Declara guerra entre duas civilizações.
        
        Args:
            civ1: Civilização declarando guerra
            civ2: Civilização alvo
        """
        self.game_controller.diplomacy_controller.declare_war(civ1, civ2)
    
    def _propose_trade(self, civ1: Civilization, civ2: Civilization) -> None:
        """
        Propõe um acordo comercial entre duas civilizações.
        
        Args:
            civ1: Civilização propondo o acordo
            civ2: Civilização alvo
        """
        # Implementação simplificada - propor troca de recursos
        if not civ1.resources or not civ2.resources:
            return
        
        # Encontrar recursos que civ1 tem e civ2 não tem
        resources_to_offer = []
        for resource in civ1.resources:
            if resource not in civ2.resources:
                resources_to_offer.append(resource)
        
        # Encontrar recursos que civ2 tem e civ1 não tem
        resources_to_request = []
        for resource in civ2.resources:
            if resource not in civ1.resources:
                resources_to_request.append(resource)
        
        # Se houver recursos para trocar, propor acordo
        if resources_to_offer and resources_to_request:
            offer_resource = random.choice(resources_to_offer)
            request_resource = random.choice(resources_to_request)
            
            self.game_controller.diplomacy_controller.propose_trade(
                civ1, civ2, 
                {"resource": offer_resource}, 
                {"resource": request_resource}
            )
    
    def _propose_friendship(self, civ1: Civilization, civ2: Civilization) -> None:
        """
        Propõe um acordo de amizade entre duas civilizações.
        
        Args:
            civ1: Civilização propondo o acordo
            civ2: Civilização alvo
        """
        self.game_controller.diplomacy_controller.declare_friendship(civ1, civ2)
    
    def _is_good_city_location(self, x: int, y: int, civ: Civilization) -> bool:
        """
        Verifica se uma posição é boa para fundar uma cidade.
        
        Args:
            x, y: Coordenadas da posição
            civ: Civilização avaliando
            
        Returns:
            True se for uma boa localização, False caso contrário
        """
        world = self.game_controller.game_state.world
        
        # Verificar se o tile é válido para cidade
        tile = world.get_tile(x, y)
        if not tile or not tile.can_found_city():
            return False
        
        # Verificar se está muito perto de outras cidades
        for city in self.game_controller.get_all_cities():
            distance = self._distance(x, y, city.x, city.y)
            if distance < 4:  # Distância mínima entre cidades
                return False
        
        # Avaliar recursos ao redor
        resource_count = 0
        food_count = 0
        production_count = 0
        
        # Verificar tiles em um raio de 2
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = x + dx, y + dy
                
                if not world.is_valid_position(nx, ny):
                    continue
                
                nearby_tile = world.get_tile(nx, ny)
                if not nearby_tile:
                    continue
                
                # Contar recursos
                if nearby_tile.resource:
                    resource_count += 1
                
                # Contar rendimentos
                food_count += nearby_tile.get_food_yield()
                production_count += nearby_tile.get_production_yield()
        
        # Critérios para uma boa localização
        has_enough_resources = resource_count >= 2
        has_enough_food = food_count >= 6
        has_enough_production = production_count >= 4
        
        return has_enough_resources and has_enough_food and has_enough_production
    
    def _find_city_location(self, civ: Civilization, unit: Unit, priorities: Dict[str, float]) -> Optional[Tuple[int, int]]:
        """
        Encontra uma boa localização para fundar uma cidade.
        
        Args:
            civ: Civilização da IA
            unit: Unidade colono
            priorities: Prioridades da IA
            
        Returns:
            Coordenadas da localização ou None se não encontrar
        """
        world = self.game_controller.game_state.world
        
        # Avaliar posições em um raio de busca
        search_radius = 10
        best_location = None
        best_score = 0
        
        for dx in range(-search_radius, search_radius + 1):
            for dy in range(-search_radius, search_radius + 1):
                nx, ny = unit.x + dx, unit.y + dy
                
                if not world.is_valid_position(nx, ny):
                    continue
                
                # Verificar se é uma boa localização
                if self._is_good_city_location(nx, ny, civ):
                    # Calcular pontuação da localização
                    score = self._evaluate_city_location(nx, ny, civ, priorities)
                    
                    # Ajustar pontuação pela distância (localizações mais próximas são preferidas)
                    distance = self._distance(unit.x, unit.y, nx, ny)
                    score = score / (1 + distance * 0.1)
                    
                    if score > best_score:
                        best_score = score
                        best_location = (nx, ny)
        
        return best_location
    
    def _evaluate_city_location(self, x: int, y: int, civ: Civilization, priorities: Dict[str, float]) -> float:
        """
        Avalia a qualidade de uma localização para cidade.
        
        Args:
            x, y: Coordenadas da posição
            civ: Civilização avaliando
            priorities: Prioridades da IA
            
        Returns:
            Pontuação da localização
        """
        world = self.game_controller.game_state.world
        score = 0.0
        
        # Avaliar recursos ao redor
        resource_score = 0
        food_score = 0
        production_score = 0
        gold_score = 0
        
        # Verificar tiles em um raio de 2
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = x + dx, y + dy
                
                if not world.is_valid_position(nx, ny):
                    continue
                
                nearby_tile = world.get_tile(nx, ny)
                if not nearby_tile:
                    continue
                
                # Pontuação para recursos
                if nearby_tile.resource:
                    resource_type = nearby_tile.get_resource_type()
                    
                    if resource_type == "luxury":
                        resource_score += 10
                    elif resource_type == "strategic":
                        resource_score += 8
                    else:  # bonus
                        resource_score += 5
                
                # Pontuação para rendimentos
                food_score += nearby_tile.get_food_yield() * 3
                production_score += nearby_tile.get_production_yield() * 2.5
                gold_score += nearby_tile.get_gold_yield() * 2
        
        # Calcular pontuação total com base nas prioridades
        score += resource_score
        score += food_score * priorities["expansion"]
        score += production_score * (priorities["military"] + priorities["economy"]) / 2
        score += gold_score * priorities["economy"]
        
        # Bônus para localizações perto de água
        if self._is_near_water(x, y, world):
            score += 20
        
        # Bônus para localizações defensivas
        if self._is_defensible_location(x, y, world):
            score += 15 * priorities["defense"]
        
        # Penalidade para localizações muito perto de outras civilizações
        for other_civ in self.game_controller.game_state.civilizations:
            if other_civ != civ:
                for city in other_civ.cities:
                    distance = self._distance(x, y, city.x, city.y)
                    if distance < 6:
                        score -= (6 - distance) * 10
        
        return score
    
    def _is_near_water(self, x: int, y: int, world) -> bool:
        """
        Verifica se uma posição está perto de água.
        
        Args:
            x, y: Coordenadas da posição
            world: Mundo do jogo
            
        Returns:
            True se estiver perto de água, False caso contrário
        """
        # Verificar tiles adjacentes
        for dx, dy in [(0, -1), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            
            if not world.is_valid_position(nx, ny):
                continue
            
            tile = world.get_tile(nx, ny)
            if tile and tile.terrain_type in ["ocean", "coast", "lake"]:
                return True
        
        return False
    
    def _is_defensible_location(self, x: int, y: int, world) -> bool:
        """
        Verifica se uma posição é defensível.
        
        Args:
            x, y: Coordenadas da posição
            world: Mundo do jogo
            
        Returns:
            True se for defensível, False caso contrário
        """
        # Contar terrenos defensivos ao redor (montanhas, colinas)
        defensive_count = 0
        
        for dx, dy in [(0, -1), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            
            if not world.is_valid_position(nx, ny):
                continue
            
            tile = world.get_tile(nx, ny)
            if tile and tile.terrain_type in ["mountain", "hills"]:
                defensive_count += 1
        
        # Considerar defensível se tiver pelo menos 2 terrenos defensivos
        return defensive_count >= 2
    
    def _should_build_improvement(self, tile, civ: Civilization, priorities: Dict[str, float]) -> bool:
        """
        Verifica se deve construir uma melhoria em um tile.
        
        Args:
            tile: Tile a ser verificado
            civ: Civilização da IA
            priorities: Prioridades da IA
            
        Returns:
            True se deve construir uma melhoria, False caso contrário
        """
        # Não construir se já tiver uma melhoria
        if tile.improvement:
            return False
        
        # Não construir em terrenos impróprios
        if tile.terrain_type in ["mountain", "ocean"]:
            return False
        
        # Verificar se há uma melhoria adequada para o terreno
        return self._choose_improvement(tile, civ, priorities) is not None
    
    def _choose_improvement(self, tile, civ: Civilization, priorities: Dict[str, float]) -> Optional[str]:
        """
        Escolhe a melhor melhoria para um tile.
        
        Args:
            tile: Tile a ser melhorado
            civ: Civilização da IA
            priorities: Prioridades da IA
            
        Returns:
            ID da melhoria ou None se não houver melhoria adequada
        """
        terrain_type = tile.terrain_type
        resource = tile.resource
        
        # Priorizar recursos
        if resource:
            resource_data = self.game_controller.data_loader.get_resource_data(resource)
            required_improvement = resource_data.get("required_improvement")
            
            if required_improvement:
                # Verificar se a civilização tem a tecnologia necessária
                tech_requirement = resource_data.get("required_tech")
                if not tech_requirement or tech_requirement in civ.technologies:
                    return required_improvement
        
        # Escolher com base no terreno e prioridades
        if terrain_type == "plains" or terrain_type == "grassland":
            if priorities["expansion"] > priorities["economy"]:
                return "farm"
            else:
                return "mine"
        elif terrain_type == "hills":
            return "mine"
        elif terrain_type == "desert":
            if priorities["economy"] > 0.6:
                return "trading_post"
            return None
        elif terrain_type == "forest":
            if priorities["production"] > priorities["economy"]:
                return "lumber_mill"
            else:
                return "trading_post"
        elif terrain_type == "jungle":
            # Remover selva para construir fazenda se prioridade de expansão for alta
            if priorities["expansion"] > 0.7:
                return "clear_jungle"
            else:
                return "trading_post"
        elif terrain_type == "tundra":
            if priorities["economy"] > 0.6:
                return "trading_post"
            return None
        
        return None
    
    def _find_tile_to_improve(self, civ: Civilization, unit: Unit, priorities: Dict[str, float]) -> Optional[Tuple[int, int]]:
        """
        Encontra um tile para melhorar.
        
        Args:
            civ: Civilização da IA
            unit: Unidade trabalhador
            priorities: Prioridades da IA
            
        Returns:
            Coordenadas do tile ou None se não encontrar
        """
        world = self.game_controller.game_state.world
        
        # Procurar tiles pertencentes à civilização
        owned_tiles = []
        
        for city in civ.cities:
            # Verificar tiles em um raio de 3 da cidade
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    nx, ny = city.x + dx, city.y + dy
                    
                    if not world.is_valid_position(nx, ny):
                        continue
                    
                    tile = world.get_tile(nx, ny)
                    if not tile or tile.owner != civ.id:
                        continue
                    
                    # Verificar se o tile pode ser melhorado
                    if self._should_build_improvement(tile, civ, priorities):
                        owned_tiles.append((nx, ny, tile))
        
        if not owned_tiles:
            return None
        
        # Avaliar cada tile
        tile_scores = []
        
        for nx, ny, tile in owned_tiles:
            # Calcular pontuação do tile
            score = self._evaluate_tile_for_improvement(tile, civ, priorities)
            
            # Ajustar pontuação pela distância (tiles mais próximos são preferidos)
            distance = self._distance(unit.x, unit.y, nx, ny)
            score = score / (1 + distance * 0.2)
            
            tile_scores.append((nx, ny, score))
        
        # Ordenar por pontuação
        tile_scores.sort(key=lambda x: x[2], reverse=True)
        
        # Retornar o melhor tile
        return (tile_scores[0][0], tile_scores[0][1])
    
    def _evaluate_tile_for_improvement(self, tile, civ: Civilization, priorities: Dict[str, float]) -> float:
        """
        Avalia a importância de melhorar um tile.
        
        Args:
            tile: Tile a ser avaliado
            civ: Civilização da IA
            priorities: Prioridades da IA
            
        Returns:
            Pontuação do tile
        """
        score = 0.0
        
        # Bônus para tiles com recursos
        if tile.resource:
            resource_data = self.game_controller.data_loader.get_resource_data(tile.resource)
            resource_type = resource_data.get("type", "bonus")
            
            if resource_type == "luxury":
                score += 30
            elif resource_type == "strategic":
                score += 25 * priorities["military"]
            else:  # bonus
                score += 15
        
        # Avaliar com base no terreno
        terrain_type = tile.terrain_type
        
        if terrain_type == "plains" or terrain_type == "grassland":
            score += 10 * priorities["expansion"]
        elif terrain_type == "hills":
            score += 15 * priorities["production"]
        elif terrain_type == "forest":
            score += 12 * priorities["production"]
        elif terrain_type == "desert":
            score += 5 * priorities["economy"]
        elif terrain_type == "tundra":
            score += 5
        
        # Bônus para tiles próximos a cidades
        nearest_city = self._find_nearest_city(civ, tile.x, tile.y)
        if nearest_city:
            distance = self._distance(tile.x, tile.y, nearest_city.x, nearest_city.y)
            score += max(0, (4 - distance) * 5)  # Maior bônus para tiles mais próximos
        
        return score
    
    def _find_nearest_city(self, civ: Civilization, x: int, y: int) -> Optional[City]:
        """
        Encontra a cidade mais próxima de uma posição.
        
        Args:
            civ: Civilização da IA
            x, y: Coordenadas da posição
            
        Returns:
            Cidade mais próxima ou None se não houver cidades
        """
        if not civ.cities:
            return None
        
        nearest_city = None
        min_distance = float('inf')
        
        for city in civ.cities:
            distance = self._distance(x, y, city.x, city.y)
            
            if distance < min_distance:
                min_distance = distance
                nearest_city = city
        
        return nearest_city
    
    def _find_nearest_enemy(self, civ: Civilization, x: int, y: int, max_range: int = 3) -> Optional[Unit]:
        """
        Encontra a unidade inimiga mais próxima.
        
        Args:
            civ: Civilização da IA
            x, y: Coordenadas da posição
            max_range: Alcance máximo de busca
            
        Returns:
            Unidade inimiga mais próxima ou None se não encontrar
        """
        nearest_enemy = None
        min_distance = float('inf')
        
        for other_civ in self.game_controller.game_state.civilizations:
            if other_civ == civ or not self._is_at_war_with(civ, other_civ):
                continue
            
            for unit in other_civ.units:
                distance = self._distance(x, y, unit.x, unit.y)
                
                if distance <= max_range and distance < min_distance:
                    min_distance = distance
                    nearest_enemy = unit
        
        return nearest_enemy
    
    def _should_attack(self, unit: Unit, enemy: Unit, priorities: Dict[str, float]) -> bool:
        """
        Decide se deve atacar uma unidade inimiga.
        
        Args:
            unit: Unidade atacante
            enemy: Unidade inimiga
            priorities: Prioridades da IA
            
        Returns:
            True se deve atacar, False caso contrário
        """
        # Verificar se tem força suficiente
        strength_ratio = unit.strength / max(1, enemy.strength)
        
        # Mais agressivo se tiver prioridade militar alta
        aggression_threshold = 1.0 - (priorities["military"] * 0.3)
        
        # Atacar se for mais forte ou se for agressivo
        return strength_ratio >= aggression_threshold
    
    def _find_military_target(self, civ: Civilization, unit: Unit, priorities: Dict[str, float]) -> Optional[Tuple[int, int]]:
        """
        Encontra um alvo militar para uma unidade.
        
        Args:
            civ: Civilização da IA
            unit: Unidade militar
            priorities: Prioridades da IA
            
        Returns:
            Coordenadas do alvo ou None se não encontrar
        """
        # Procurar cidades inimigas
        enemy_cities = []
        
        for other_civ in self.game_controller.game_state.civilizations:
            if other_civ == civ or not self._is_at_war_with(civ, other_civ):
                continue
            
            for city in other_civ.cities:
                distance = self._distance(unit.x, unit.y, city.x, city.y)
                enemy_cities.append((city.x, city.y, distance))
        
        # Procurar unidades inimigas
        enemy_units = []
        
        for other_civ in self.game_controller.game_state.civilizations:
            if other_civ == civ or not self._is_at_war_with(civ, other_civ):
                continue
            
            for enemy in other_civ.units:
                distance = self._distance(unit.x, unit.y, enemy.x, enemy.y)
                
                # Priorizar unidades mais fracas
                strength_ratio = unit.strength / max(1, enemy.strength)
                enemy_units.append((enemy.x, enemy.y, distance, strength_ratio))
        
        # Decidir entre atacar cidade ou unidade
        if priorities["military"] > priorities["defense"]:
            # Modo ofensivo: priorizar cidades
            if enemy_cities:
                # Ordenar por distância
                enemy_cities.sort(key=lambda x: x[2])
                return (enemy_cities[0][0], enemy_cities[0][1])
            
            if enemy_units:
                # Ordenar por uma combinação de distância e força relativa
                enemy_units.sort(key=lambda x: x[2] / x[3])
                return (enemy_units[0][0], enemy_units[0][1])
        else:
            # Modo defensivo: priorizar unidades
            if enemy_units:
                # Ordenar por uma combinação de distância e força relativa
                enemy_units.sort(key=lambda x: x[2] / x[3])
                return (enemy_units[0][0], enemy_units[0][1])
            
            if enemy_cities:
                # Ordenar por distância
                enemy_cities.sort(key=lambda x: x[2])
                return (enemy_cities[0][0], enemy_cities[0][1])
        
        return None
    
    def _find_border_position(self, civ: Civilization, unit: Unit) -> Optional[Tuple[int, int]]:
        """
        Encontra uma posição de fronteira para uma unidade militar.
        
        Args:
            civ: Civilização da IA
            unit: Unidade militar
            
        Returns:
            Coordenadas da posição ou None se não encontrar
        """
        world = self.game_controller.game_state.world
        
        # Encontrar tiles de fronteira
        border_tiles = []
        
        for x in range(world.width):
            for y in range(world.height):
                tile = world.get_tile(x, y)
                
                if not tile or tile.owner != civ.id:
                    continue
                
                # Verificar se é um tile de fronteira
                is_border = False
                
                for dx, dy in [(0, -1), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)]:
                    nx, ny = x + dx, y + dy
                    
                    if not world.is_valid_position(nx, ny):
                        continue
                    
                    neighbor = world.get_tile(nx, ny)
                    
                    if not neighbor or (neighbor.owner and neighbor.owner != civ.id):
                        is_border = True
                        break
                
                if is_border:
                    # Calcular distância
                    distance = self._distance(unit.x, unit.y, x, y)
                    border_tiles.append((x, y, distance))
        
        if not border_tiles:
            return None
        
        # Ordenar por distância
        border_tiles.sort(key=lambda x: x[2])
        
        # Retornar a posição mais próxima
        return (border_tiles[0][0], border_tiles[0][1])
    
    def _distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calcula a distância entre duas posições.
        
        Args:
            x1, y1: Coordenadas da primeira posição
            x2, y2: Coordenadas da segunda posição
            
        Returns:
            Distância entre as posições
        """
        # Distância euclidiana simples
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    def _on_civ_turn_start(self, event_data: Dict[str, Any]) -> None:
        """
        Manipulador de evento para início de turno de civilização.
        
        Args:
            event_data: Dados do evento
        """
        civ_id = event_data.get("civ_id")
        
        if not civ_id:
            return
        
        # Encontrar a civilização
        civ = None
        for c in self.game_controller.game_state.civilizations:
            if c.id == civ_id:
                civ = c
                break
        
        if not civ or civ == self.game_controller.game_state.player_civ:
            return
        
        # Processar turno da IA
        self.process_ai_turn(civ)