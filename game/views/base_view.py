# game/views/base_view.py
import curses
import logging

class BaseView:
    """
    Classe base para todas as visualizações do jogo.
    
    Esta classe fornece funcionalidades comuns a todas as visualizações,
    como renderização, manipulação de entrada e gerenciamento de janelas.
    """
    
    def __init__(self, stdscr):
        """
        Inicializa uma nova visualização.
        
        Args:
            stdscr: Objeto de tela do curses.
        """
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def clear(self):
        """Limpa a tela."""
        self.stdscr.clear()
        
    def refresh(self):
        """Atualiza a tela."""
        self.stdscr.refresh()
        
    def get_input(self):
        """
        Obtém entrada do usuário.
        
        Returns:
            int: Código da tecla pressionada.
        """
        return self.stdscr.getch()
    
    def add_str(self, y, x, text, attr=0):
        """
        Adiciona uma string à tela na posição especificada.
        
        Args:
            y (int): Coordenada Y (linha).
            x (int): Coordenada X (coluna).
            text (str): Texto a ser exibido.
            attr: Atributos de exibição (cores, negrito, etc).
            
        Returns:
            bool: True se bem-sucedido, False se fora dos limites.
        """
        try:
            if y < 0 or y >= self.height or x < 0:
                self.logger.warning(f"Tentativa de escrever fora dos limites: ({x}, {y})")
                return False
                
            # Trunca o texto se ele ultrapassar a largura da tela
            max_length = self.width - x
            if max_length <= 0:
                return False
                
            if len(text) > max_length:
                text = text[:max_length]
                
            self.stdscr.addstr(y, x, text, attr)
            return True
        except curses.error:
            self.logger.error(f"Erro ao adicionar string: ({x}, {y}) '{text}'", exc_info=True)
            return False
    
    def show_message(self, message, wait_for_key=True):
        """
        Exibe uma mensagem centralizada na tela.
        
        Args:
            message (str): Mensagem a ser exibida.
            wait_for_key (bool): Se True, aguarda o usuário pressionar uma tecla.
            
        Returns:
            int or None: Código da tecla pressionada se wait_for_key=True, None caso contrário.
        """
        self.clear()
        lines = message.strip().split('\n')
        start_y = (self.height - len(lines)) // 2
        
        for i, line in enumerate(lines):
            start_x = (self.width - len(line)) // 2
            self.add_str(start_y + i, start_x, line)
            
        if wait_for_key:
            self.add_str(start_y + len(lines) + 2, (self.width - 36) // 2, 
                        "Pressione qualquer tecla para continuar...")
            self.refresh()
            return self.get_input()
        else:
            self.refresh()
            return None
    
    def create_window(self, height, width, y, x):
        """
        Cria uma nova janela.
        
        Args:
            height (int): Altura da janela.
            width (int): Largura da janela.
            y (int): Coordenada Y do canto superior esquerdo.
            x (int): Coordenada X do canto superior esquerdo.
            
        Returns:
            window: Objeto de janela do curses.
        """
        try:
            return curses.newwin(height, width, y, x)
        except curses.error:
            self.logger.error(f"Erro ao criar janela: {height}x{width} em ({x}, {y})", exc_info=True)
            return None
