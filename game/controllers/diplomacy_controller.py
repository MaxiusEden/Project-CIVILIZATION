"""
Controlador responsável por gerenciar a diplomacia entre civilizações.
"""
import logging
import random
from typing import Dict, Any, List, Optional, Tuple

from game.models.civilization import Civilization
from game.utils.event_bus import EventBus

class DiplomacyController:
    """
    Gerencia as relações diplomáticas entre civilizações, incluindo
    acordos, guerras, trocas e outros aspectos diplomáticos.
    """
    
    def __init__(self, game_controller, event_bus: Optional[EventBus] = None):
        """
        Inicializa o controlador de diplomacia.
        
        Args:
            game_controller: Referência ao controlador principal do jogo
            event_bus: Barramento de eventos para comunicação (opcional)
        """
        self.logger = logging.getLogger(__name__)
        self.game_controller = game_controller
        self.event_bus = event_bus or EventBus()
        
        # Registrar para eventos relevantes
        if event_bus:
            self.event_bus.subscribe("turn.end", self._on_turn_end)
    
    def declare_war(self, civ1: Civilization, civ2: Civilization) -> bool:
        """
        Declara guerra entre duas civilizações.
        
        Args:
            civ1: Civilização declarando guerra
            civ2: Civilização alvo
            
        Returns:
            True se a guerra foi declarada com sucesso, False caso contrário
        """
        if civ1 == civ2:
            self.logger.warning("Uma civilização não pode declarar guerra contra si mesma")
            return False
        
        # Verificar se já estão em guerra
        if civ2.id in civ1.at_war_with:
            self.logger.info(f"Civilizações {civ1.name} e {civ2.name} já estão em guerra")
            return False
        
        # Cancelar acordos existentes
        self._cancel_agreements(civ1, civ2)
        
        # Declarar guerra
        civ1.at_war_with.append(civ2.id)
        civ2.at_war_with.append(civ1.id)
        
        # Registrar no histórico
        if civ2.id not in civ1.war_history:
            civ1.war_history.append(civ2.id)
        
        if civ1.id not in civ2.war_history:
            civ2.war_history.append(civ1.id)
        
        # Disparar evento
        self.event_bus.publish("diplomacy.war_declared", {
            "aggressor_id": civ1.id,
            "defender_id": civ2.id
        })
        
        self.logger.info(f"Guerra declarada: {civ1.name} contra {civ2.name}")
        return True
    
    def make_peace(self, civ1: Civilization, civ2: Civilization) -> bool:
        """
        Estabelece paz entre duas civilizações.
        
        Args:
            civ1: Primeira civilização
            civ2: Segunda civilização
            
        Returns:
            True se a paz foi estabelecida com sucesso, False caso contrário
        """
        if civ1 == civ2:
            self.logger.warning("Uma civilização não pode fazer paz consigo mesma")
            return False
        
        # Verificar se estão em guerra
        if civ2.id not in civ1.at_war_with:
            self.logger.info(f"Civilizações {civ1.name} e {civ2.name} não estão em guerra")
            return False
        
        # Estabelecer paz
        civ1.at_war_with.remove(civ2.id)
        civ2.at_war_with.remove(civ1.id)
        
        # Adicionar período de trégua
        civ1.truces[civ2.id] = self.game_controller.game_state.current_turn + 10
        civ2.truces[civ1.id] = self.game_controller.game_state.current_turn + 10
        
        # Disparar evento
        self.event_bus.publish("diplomacy.peace_made", {
            "civ1_id": civ1.id,
            "civ2_id": civ2.id
        })
        
        self.logger.info(f"Paz estabelecida entre {civ1.name} e {civ2.name}")
        return True
    
    def declare_friendship(self, civ1: Civilization, civ2: Civilization) -> bool:
        """
        Declara amizade entre duas civilizações.
        
        Args:
            civ1: Primeira civilização
            civ2: Segunda civilização
            
        Returns:
            True se a amizade foi declarada com sucesso, False caso contrário
        """
        if civ1 == civ2:
            self.logger.warning("Uma civilização não pode declarar amizade consigo mesma")
            return False
        
        # Verificar se estão em guerra
        if civ2.id in civ1.at_war_with:
            self.logger.warning(f"Civilizações {civ1.name} e {civ2.name} estão em guerra")
            return False
        
        # Verificar se já são amigas
        if civ2.id in civ1.friendships:
            self.logger.info(f"Civilizações {civ1.name} e {civ2.name} já são amigas")
            return False
        
        # Declarar amizade
        civ1.friendships[civ2.id] = self.game_controller.game_state.current_turn + 30
        civ2.friendships[civ1.id] = self.game_controller.game_state.current_turn + 30
        
        # Disparar evento
        self.event_bus.publish("diplomacy.friendship_declared", {
            "civ1_id": civ1.id,
            "civ2_id": civ2.id
        })
        
        self.logger.info(f"Amizade declarada entre {civ1.name} e {civ2.name}")
        return True
    
    def denounce(self, civ1: Civilization, civ2: Civilization) -> bool:
        """
        Denuncia uma civilização.
        
        Args:
            civ1: Civilização que denuncia
            civ2: Civilização denunciada
            
        Returns:
            True se a denúncia foi feita com sucesso, False caso contrário
        """
        if civ1 == civ2:
            self.logger.warning("Uma civilização não pode denunciar a si mesma")
            return False
        
        # Verificar se já denunciou
        if civ2.id in civ1.denounced:
            self.logger.info(f"{civ1.name} já denunciou {civ2.name}")
            return False
        
        # Cancelar amizade se existir
        if civ2.id in civ1.friendships:
            del civ1.friendships[civ2.id]
            del civ2.friendships[civ1.id]
        
        # Denunciar
        civ1.denounced[civ2.id] = self.game_controller.game_state.current_turn + 20
        
        # Disparar evento
        self.event_bus.publish("diplomacy.denounced", {
            "civ1_id": civ1.id,
            "civ2_id": civ2.id
        })
        
        self.logger.info(f"{civ1.name} denunciou {civ2.name}")
        return True
    
    def propose_trade(self, civ1: Civilization, civ2: Civilization, offer: Dict[str, Any], request: Dict[str, Any]) -> bool:
        """
        Propõe um acordo comercial entre duas civilizações.
        
        Args:
            civ1: Civilização propondo o acordo
            civ2: Civilização alvo
            offer: O que civ1 está oferecendo
            request: O que civ1 está pedindo
            
        Returns:
            True se o acordo foi aceito, False caso contrário
        """
        if civ1 == civ2:
            self.logger.warning("Uma civilização não pode negociar consigo mesma")
            return False
        
        # Verificar se estão em guerra
        if civ2.id in civ1.at_war_with:
            self.logger.warning(f"Civilizações {civ1.name} e {civ2.name} estão em guerra")
            return False
        
        # Avaliar o acordo (para IA)
        if civ2 != self.game_controller.game_state.player_civ:
            # Lógica de avaliação para IA
            deal_value = self._evaluate_trade_deal(civ2, offer, request)
            
            # IA aceita se o valor for positivo
            if deal_value <= 0:
                self.logger.info(f"{civ2.name} rejeitou o acordo comercial de {civ1.name}")
                return False
        
        # Processar o acordo
        self._process_trade_deal(civ1, civ2, offer, request)
        
        # Registrar o acordo
        trade_id = f"trade_{civ1.id}_{civ2.id}_{self.game_controller.game_state.current_turn}"
        
        civ1.trade_agreements[trade_id] = {
            "partner": civ2.id,
            "offer": offer,
            "request": request,
            "start_turn": self.game_controller.game_state.current_turn,
            "duration": 30  # 30 turnos por padrão
        }
        
        civ2.trade_agreements[trade_id] = {
            "partner": civ1.id,
            "offer": request,  # Invertido para a perspectiva de civ2
            "request": offer,  # Invertido para a perspectiva de civ2
            "start_turn": self.game_controller.game_state.current_turn,
            "duration": 30
        }
        
        # Disparar evento
        self.event_bus.publish("diplomacy.trade_accepted", {
            "civ1_id": civ1.id,
            "civ2_id": civ2.id,
            "trade_id": trade_id
        })
        
        self.logger.info(f"Acordo comercial estabelecido entre {civ1.name} e {civ2.name}")
        return True
    
    def cancel_trade(self, trade_id: str) -> bool:
        """
        Cancela um acordo comercial.
        
        Args:
            trade_id: ID do acordo comercial
            
        Returns:
            True se o acordo foi cancelado com sucesso, False caso contrário
        """
        # Encontrar as civilizações envolvidas
        civ1 = None
        civ2 = None
        
        for civ in self.game_controller.game_state.civilizations:
            if trade_id in civ.trade_agreements:
                if civ1 is None:
                    civ1 = civ
                else:
                    civ2 = civ
                    break
        
        if civ1 is None or civ2 is None:
            self.logger.warning(f"Acordo comercial {trade_id} não encontrado")
            return False
        
        # Cancelar o acordo
        del civ1.trade_agreements[trade_id]
        del civ2.trade_agreements[trade_id]
        
        # Disparar evento
        self.event_bus.publish("diplomacy.trade_cancelled", {
            "civ1_id": civ1.id,
            "civ2_id": civ2.id,
            "trade_id": trade_id
        })
        
        self.logger.info(f"Acordo comercial {trade_id} cancelado")
        return True
    
    def get_relation_status(self, civ1: Civilization, civ2: Civilization) -> Dict[str, Any]:
        """
        Obtém o status da relação entre duas civilizações.
        
        Args:
            civ1: Primeira civilização
            civ2: Segunda civilização
            
        Returns:
            Dicionário com o status da relação
        """
        status = {
            "at_war": civ2.id in civ1.at_war_with,
            "friendship": civ2.id in civ1.friendships,
            "denounced": civ2.id in civ1.denounced,
            "truce": civ2.id in civ1.truces,
            "trade_agreements": [],
            "opinion": self._calculate_opinion(civ1, civ2)
        }
        
        # Listar acordos comerciais
        for trade_id, trade_info in civ1.trade_agreements.items():
            if trade_info["partner"] == civ2.id:
                status["trade_agreements"].append({
                    "id": trade_id,
                    "offer": trade_info["offer"],
                    "request": trade_info["request"],
                    "turns_remaining": trade_info["start_turn"] + trade_info["duration"] - self.game_controller.game_state.current_turn
                })
        
        return status
    
    def get_all_relations(self, civ: Civilization) -> Dict[str, Dict[str, Any]]:
        """
        Obtém o status de todas as relações de uma civilização.
        
        Args:
            civ: Civilização
            
        Returns:
            Dicionário com o status de todas as relações
        """
        relations = {}
        
        for other_civ in self.game_controller.game_state.civilizations:
            if other_civ != civ:
                relations[other_civ.id] = self.get_relation_status(civ, other_civ)
        
        return relations
    
    def _cancel_agreements(self, civ1: Civilization, civ2: Civilization) -> None:
        """
        Cancela todos os acordos entre duas civilizações.
        
        Args:
            civ1: Primeira civilização
            civ2: Segunda civilização
        """
        # Cancelar amizade
        if civ2.id in civ1.friendships:
            del civ1.friendships[civ2.id]
            del civ2.friendships[civ1.id]
        
        # Cancelar acordos comerciais
        trade_ids_to_cancel = []
        
        for trade_id, trade_info in civ1.trade_agreements.items():
            if trade_info["partner"] == civ2.id:
                trade_ids_to_cancel.append(trade_id)
        
        for trade_id in trade_ids_to_cancel:
            self.cancel_trade(trade_id)
    
    def _evaluate_trade_deal(self, civ: Civilization, offer: Dict[str, Any], request: Dict[str, Any]) -> float:
        """
        Avalia o valor de um acordo comercial para uma civilização.
        
        Args:
            civ: Civilização avaliando o acordo
            offer: O que está sendo oferecido
            request: O que está sendo pedido
            
        Returns:
            Valor do acordo (positivo se for bom para a civilização)
        """
        offer_value = 0.0
        request_value = 0.0
        
        # Avaliar oferta
        if "gold" in offer:
            offer_value += offer["gold"]
        
        if "gold_per_turn" in offer:
            offer_value += offer["gold_per_turn"] * 10  # Valor de 10 turnos
        
        if "resource" in offer:
            resource = offer["resource"]
            resource_data = self.game_controller.data_loader.get_resource_data(resource)
            
            if resource_data["type"] == "luxury":
                offer_value += 100
            elif resource_data["type"] == "strategic":
                offer_value += 80
            else:  # bonus
                offer_value += 50
        
        # Avaliar pedido
        if "gold" in request:
            request_value += request["gold"]
        
        if "gold_per_turn" in request:
            request_value += request["gold_per_turn"] * 10  # Valor de 10 turnos
        
        if "resource" in request:
            resource = request["resource"]
            resource_data = self.game_controller.data_loader.get_resource_data(resource)
            
            if resource_data["type"] == "luxury":
                request_value += 100
            elif resource_data["type"] == "strategic":
                request_value += 80
            else:  # bonus
                request_value += 50
            
            # Recursos estratégicos são mais valiosos se a civilização estiver em guerra
            if resource_data["type"] == "strategic" and civ.at_war_with:
                request_value += 40
        
        # Calcular valor líquido
        net_value = offer_value - request_value
        
        # Ajustar com base na opinião
        opinion_modifier = 1.0
        
        # Se a civilização que oferece for amiga, o acordo é mais atraente
        if "civ_id" in offer and offer["civ_id"] in civ.friendships:
            opinion_modifier = 1.2
        
        # Se a civilização que oferece for denunciada, o acordo é menos atraente
        if "civ_id" in offer and offer["civ_id"] in civ.denounced:
            opinion_modifier = 0.8
        
        return net_value * opinion_modifier
    
    def _process_trade_deal(self, civ1: Civilization, civ2: Civilization, offer: Dict[str, Any], request: Dict[str, Any]) -> None:
        """
        Processa um acordo comercial entre duas civilizações.
        
        Args:
            civ1: Civilização que oferece
            civ2: Civilização que recebe
            offer: O que civ1 está oferecendo
            request: O que civ1 está pedindo
        """
        # Processar o que civ1 oferece para civ2
        if "gold" in offer:
            civ1.gold -= offer["gold"]
            civ2.gold += offer["gold"]
        
        if "gold_per_turn" in offer:
            # Isso será processado a cada turno
            pass
        
        if "resource" in offer:
            resource = offer["resource"]
            # Transferir acesso ao recurso (não a posse do tile)
            if resource in civ1.resources and resource not in civ2.resources:
                civ2.resources.append(resource)
        
        # Processar o que civ2 oferece para civ1
        if "gold" in request:
            civ2.gold -= request["gold"]
            civ1.gold += request["gold"]
        
        if "gold_per_turn" in request:
            # Isso será processado a cada turno
            pass
        
        if "resource" in request:
            resource = request["resource"]
            # Transferir acesso ao recurso (não a posse do tile)
            if resource in civ2.resources and resource not in civ1.resources:
                civ1.resources.append(resource)
    
    def _calculate_opinion(self, civ1: Civilization, civ2: Civilization) -> int:
        """
        Calcula a opinião de uma civilização sobre outra.
        
        Args:
            civ1: Civilização que tem a opinião
            civ2: Civilização alvo da opinião
            
        Returns:
            Valor da opinião (negativo para ruim, positivo para bom)
        """
        opinion = 0
        
        # Base inicial
        opinion += 10  # Ligeiramente positivo por padrão
        
        # Modificadores de relação
        if civ2.id in civ1.at_war_with:
            opinion -= 100
        
        if civ2.id in civ1.friendships:
            opinion += 50
        
        if civ2.id in civ1.denounced:
            opinion -= 50
        
        if civ2.id in civ1.truces:
            opinion -= 20  # Ainda há ressentimento após uma guerra
        
        # Acordos comerciais melhoram a opinião
        for trade_info in civ1.trade_agreements.values():
            if trade_info["partner"] == civ2.id:
                opinion += 10
        
        # Histórico de guerra
        if civ2.id in civ1.war_history:
            opinion -= 30
        
        # Personalidade da civilização afeta a opinião
        if civ1.personality == "friendly":
            opinion += 10
        elif civ1.personality == "aggressive":
            opinion -= 10
        
        # Competição por recursos e terras
        if self._are_competing_for_land(civ1, civ2):
            opinion -= 20
        
        # Diferença de força militar
        military_diff = self._get_military_strength(civ1) - self._get_military_strength(civ2)
        if military_diff < 0:
            # Civilizações mais fracas temem as mais fortes
            opinion -= min(30, abs(military_diff) // 10)
        
        # Adicionar um pouco de aleatoriedade
        opinion += random.randint(-5, 5)
        
        return opinion
    
    def _are_competing_for_land(self, civ1: Civilization, civ2: Civilization) -> bool:
        """
        Verifica se duas civilizações estão competindo por terras.
        
        Args:
            civ1: Primeira civilização
            civ2: Segunda civilização
            
        Returns:
            True se estiverem competindo, False caso contrário
        """
        # Verificar se as civilizações têm cidades próximas
        for city1 in civ1.cities:
            for city2 in civ2.cities:
                distance = self._distance(city1.x, city1.y, city2.x, city2.y)
                if distance < 10:  # Distância arbitrária para considerar competição
                    return True
        
        return False
    
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
    
    def _distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calcula a distância entre duas posições.
        
        Args:
            x1, y1: Coordenadas da primeira posição
            x2, y2: Coordenadas da segunda posição
            
        Returns:
            Distância entre as posições
        """
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    def _on_turn_end(self, event_data: Dict[str, Any]) -> None:
        """
        Manipulador de evento para fim de turno.
        
        Args:
            event_data: Dados do evento
        """
        # Processar acordos comerciais por turno
        self._process_per_turn_trades()
        
        # Atualizar relações diplomáticas
        self._update_diplomatic_relations()
    
    def _process_per_turn_trades(self) -> None:
        """
        Processa os pagamentos por turno dos acordos comerciais.
        """
        for civ in self.game_controller.game_state.civilizations:
            for trade_id, trade_info in civ.trade_agreements.items():
                partner_id = trade_info["partner"]
                partner = None
                
                # Encontrar a civilização parceira
                for c in self.game_controller.game_state.civilizations:
                    if c.id == partner_id:
                        partner = c
                        break
                
                if not partner:
                    continue
                
                # Processar pagamentos por turno
                if "gold_per_turn" in trade_info["offer"]:
                    gold_amount = trade_info["offer"]["gold_per_turn"]
                    if civ.gold >= gold_amount:
                        civ.gold -= gold_amount
                        partner.gold += gold_amount
                    else:
                        # Cancelar acordo se não puder pagar
                        self.cancel_trade(trade_id)
                        self.logger.info(f"{civ.name} não pode pagar {gold_amount} de ouro por turno para {partner.name}")
                
                # Verificar se o acordo expirou
                current_turn = self.game_controller.game_state.current_turn
                if current_turn >= trade_info["start_turn"] + trade_info["duration"]:
                    self.cancel_trade(trade_id)
    
    def _update_diplomatic_relations(self) -> None:
        """
        Atualiza as relações diplomáticas entre civilizações.
        """
        current_turn = self.game_controller.game_state.current_turn
        
        for civ in self.game_controller.game_state.civilizations:
            # Remover amizades expiradas
            expired_friendships = []
            for friend_id, expiry_turn in civ.friendships.items():
                if current_turn >= expiry_turn:
                    expired_friendships.append(friend_id)
            
            for friend_id in expired_friendships:
                del civ.friendships[friend_id]
                
                # Encontrar a civilização amiga
                for friend in self.game_controller.game_state.civilizations:
                    if friend.id == friend_id:
                        if civ.id in friend.friendships:
                            del friend.friendships[civ.id]
                        break
            
            # Remover denúncias expiradas
            expired_denouncements = []
            for denounced_id, expiry_turn in civ.denounced.items():
                if current_turn >= expiry_turn:
                    expired_denouncements.append(denounced_id)
            
            for denounced_id in expired_denouncements:
                del civ.denounced[denounced_id]
            
            # Remover tréguas expiradas
            expired_truces = []
            for truce_id, expiry_turn in civ.truces.items():
                if current_turn >= expiry_turn:
                    expired_truces.append(truce_id)
            
            for truce_id in expired_truces:
                del civ.truces[truce_id]