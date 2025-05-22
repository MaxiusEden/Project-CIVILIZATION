"""
Sistema de eventos para comunicação entre componentes do jogo.
"""
import logging
from typing import Dict, List, Callable, Any

class EventBus:
    """
    Implementa um sistema de publicação/assinatura para eventos do jogo.
    
    Permite que componentes publiquem eventos e se inscrevam para receber
    notificações quando eventos específicos ocorrerem.
    """
    
    def __init__(self):
        """Inicializa o barramento de eventos."""
        self.subscribers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Inscreve uma função de callback para um tipo de evento.
        
        Args:
            event_type: Tipo de evento para se inscrever
            callback: Função a ser chamada quando o evento ocorrer
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)
            self.logger.debug(f"Inscrito em evento '{event_type}': {callback.__name__}")
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Cancela a inscrição de uma função de callback para um tipo de evento.
        
        Args:
            event_type: Tipo de evento para cancelar a inscrição
            callback: Função a ser removida
        """
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            self.logger.debug(f"Cancelada inscrição em evento '{event_type}': {callback.__name__}")
    
    def publish(self, event_type: str, event_data: Dict[str, Any] = None) -> None:
        """
        Publica um evento para todos os inscritos.
        
        Args:
            event_type: Tipo de evento a ser publicado
            event_data: Dados associados ao evento (opcional)
        """
        if event_data is None:
            event_data = {}
        
        # Adicionar o tipo de evento aos dados
        event_data["event_type"] = event_type
        
        self.logger.debug(f"Publicando evento '{event_type}'")
        
        # Notificar inscritos diretos
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    self.logger.error(f"Erro ao processar evento '{event_type}' em {callback.__name__}: {e}")
        
        # Notificar inscritos em todos os eventos
        if "*" in self.subscribers:
            for callback in self.subscribers["*"]:
                try:
                    callback(event_data)
                except Exception as e:
                    self.logger.error(f"Erro ao processar evento '{event_type}' em {callback.__name__}: {e}")
    
    def clear_all(self) -> None:
        """Remove todas as inscrições."""
        self.subscribers.clear()
        self.logger.debug("Todas as inscrições foram removidas")
    
    def clear_event(self, event_type: str) -> None:
        """
        Remove todas as inscrições para um tipo de evento específico.
        
        Args:
            event_type: Tipo de evento para limpar
        """
        if event_type in self.subscribers:
            self.subscribers.pop(event_type)
            self.logger.debug(f"Todas as inscrições para o evento '{event_type}' foram removidas")
