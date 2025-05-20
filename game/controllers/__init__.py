# game/controllers/__init__.py
import logging

class BaseController:
    """
    Classe base para todos os controladores do jogo.
    
    Esta classe fornece funcionalidades comuns a todos os controladores,
    como logging e gerenciamento de modelos.
    """
    
    def __init__(self):
        """Inicializa um novo controlador."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def handle_input(self, key):
        """
        Processa entrada do usuário.
        
        Args:
            key (int): Código da tecla pressionada.
            
        Returns:
            bool: True se a entrada foi processada, False caso contrário.
        """
        self.logger.debug(f"Tecla pressionada: {key}")
        return False
    
    def update(self):
        """
        Atualiza o estado do controlador.
        
        Este método deve ser chamado a cada ciclo do loop principal.
        """
        pass
