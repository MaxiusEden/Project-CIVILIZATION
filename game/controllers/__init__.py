# game/controllers/__init__.py
import logging
from typing import Dict, Any, Optional, List, Callable
from game.utils.event_bus import EventBus

class BaseController:
    """
    Classe base para todos os controladores do jogo.
    
    Esta classe fornece funcionalidades comuns a todos os controladores,
    como logging, gerenciamento de eventos e acesso a recursos compartilhados.
    Implementa o padrão Observer para comunicação entre controladores.
    """
    
    def __init__(self, game_controller=None, event_bus: Optional[EventBus] = None):
        """
        Inicializa um novo controlador.
        
        Args:
            game_controller: Referência ao controlador principal do jogo (opcional)
            event_bus: Barramento de eventos para comunicação (opcional)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.game_controller = game_controller
        self.event_bus = event_bus or EventBus()
        self.subscribed_events = []
        self._is_initialized = False
        self._event_handlers = {}
        
    def initialize(self) -> None:
        """
        Inicializa o controlador. Este método deve ser chamado após a criação
        do controlador e antes de seu uso.
        
        Subclasses devem sobrescrever este método para realizar inicializações
        específicas, mas devem chamar super().initialize().
        """
        if self._is_initialized:
            self.logger.warning(f"{self.__class__.__name__} já foi inicializado")
            return
        
        self._register_event_handlers()
        self._is_initialized = True
        self.logger.debug(f"{self.__class__.__name__} inicializado")
    
    def shutdown(self) -> None:
        """
        Finaliza o controlador, liberando recursos e cancelando inscrições de eventos.
        
        Subclasses devem sobrescrever este método para realizar limpezas
        específicas, mas devem chamar super().shutdown().
        """
        if not self._is_initialized:
            return
        
        # Cancelar todas as inscrições de eventos
        for event_type in self.subscribed_events:
            self.event_bus.unsubscribe(event_type, self._dispatch_event)
        
        self.subscribed_events = []
        self._is_initialized = False
        self.logger.debug(f"{self.__class__.__name__} finalizado")
    
    def handle_input(self, key) -> bool:
        """
        Processa entrada do usuário.
        
        Args:
            key (int): Código da tecla pressionada.
            
        Returns:
            bool: True se a entrada foi processada, False caso contrário.
        """
        self.logger.debug(f"Tecla pressionada: {key}")
        return False
    
    def update(self, delta_time: float = 0) -> None:
        """
        Atualiza o estado do controlador.
        
        Este método deve ser chamado a cada ciclo do loop principal.
        
        Args:
            delta_time: Tempo decorrido desde a última atualização (em segundos)
        """
        pass
    
    def subscribe_to_event(self, event_type: str) -> None:
        """
        Inscreve o controlador para receber notificações de um tipo de evento.
        
        Args:
            event_type: Tipo de evento para se inscrever
        """
        if event_type not in self.subscribed_events:
            self.event_bus.subscribe(event_type, self._dispatch_event)
            self.subscribed_events.append(event_type)
            self.logger.debug(f"Inscrito em evento: {event_type}")
    
    def unsubscribe_from_event(self, event_type: str) -> None:
        """
        Cancela a inscrição do controlador para um tipo de evento.
        
        Args:
            event_type: Tipo de evento para cancelar a inscrição
        """
        if event_type in self.subscribed_events:
            self.event_bus.unsubscribe(event_type, self._dispatch_event)
            self.subscribed_events.remove(event_type)
            self.logger.debug(f"Cancelada inscrição em evento: {event_type}")
    
    def publish_event(self, event_type: str, event_data: Dict[str, Any] = None) -> None:
        """
        Publica um evento para todos os inscritos.
        
        Args:
            event_type: Tipo de evento a ser publicado
            event_data: Dados associados ao evento (opcional)
        """
        if event_data is None:
            event_data = {}
        
        # Adicionar informações do controlador que está publicando o evento
        event_data["publisher"] = self.__class__.__name__
        
        self.event_bus.publish(event_type, event_data)
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Registra um manipulador para um tipo específico de evento.
        
        Args:
            event_type: Tipo de evento a ser manipulado
            handler: Função que manipula o evento
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        if handler not in self._event_handlers[event_type]:
            self._event_handlers[event_type].append(handler)
            self.logger.debug(f"Manipulador registrado para evento: {event_type}")
            
            # Inscrever-se automaticamente no evento
            self.subscribe_to_event(event_type)
    
    def unregister_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Remove um manipulador de um tipo específico de evento.
        
        Args:
            event_type: Tipo de evento
            handler: Função que manipula o evento
        """
        if event_type in self._event_handlers and handler in self._event_handlers[event_type]:
            self._event_handlers[event_type].remove(handler)
            self.logger.debug(f"Manipulador removido para evento: {event_type}")
            
            # Se não houver mais manipuladores, cancelar a inscrição
            if not self._event_handlers[event_type]:
                self.unsubscribe_from_event(event_type)
    
    def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        """
        Distribui um evento para os manipuladores apropriados.
        
        Args:
            event_data: Dados do evento
        """
        event_type = event_data.get("event_type")
        
        if not event_type:
            self.logger.warning("Evento recebido sem tipo")
            return
        
        # Chamar manipuladores específicos para este tipo de evento
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.logger.error(f"Erro ao processar evento '{event_type}' em {handler.__name__}: {e}")
        
        # Chamar manipulador genérico, se existir
        if "*" in self._event_handlers:
            for handler in self._event_handlers["*"]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.logger.error(f"Erro ao processar evento '{event_type}' em {handler.__name__}: {e}")
    
    def _register_event_handlers(self) -> None:
        """
        Registra manipuladores de eventos baseados em métodos da classe.
        
        Este método procura métodos com o prefixo 'on_' e os registra como
        manipuladores para os eventos correspondentes.
        """
        for attr_name in dir(self):
            if attr_name.startswith('on_'):
                event_type = attr_name[3:].replace('_', '.')
                handler = getattr(self, attr_name)
                
                if callable(handler):
                    self.register_event_handler(event_type, handler)
    
    def get_game_state(self) -> Any:
        """
        Obtém o estado atual do jogo.
        
        Returns:
            O estado atual do jogo ou None se não disponível
        """
        if self.game_controller:
            return self.game_controller.get_game_state()
        return None
    
    def get_data_loader(self) -> Any:
        """
        Obtém o carregador de dados do jogo.
        
        Returns:
            O carregador de dados ou None se não disponível
        """
        if self.game_controller:
            return self.game_controller.data_loader
        return None
    
    def get_config(self) -> Dict[str, Any]:
        """
        Obtém a configuração do jogo.
        
        Returns:
            Configuração do jogo ou dicionário vazio se não disponível
        """
        if self.game_controller:
            return self.game_controller.config
        return {}
    
    def log_action(self, action: str, details: Dict[str, Any] = None) -> None:
        """
        Registra uma ação do controlador no log.
        
        Args:
            action: Descrição da ação
            details: Detalhes adicionais da ação (opcional)
        """
        if details is None:
            details = {}
        
        self.logger.info(f"Ação: {action} - {details}")
        
        # Publicar evento de ação
        self.publish_event("controller.action", {
            "controller": self.__class__.__name__,
            "action": action,
            "details": details
        })
