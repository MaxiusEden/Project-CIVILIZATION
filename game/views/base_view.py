# game/views/base_view.py
import os
import sys
import logging

class BaseView:
    """
    Classe base para todas as visualizações.
    
    Fornece métodos comuns para exibição de informações e interação com o usuário.
    """
    
    def __init__(self):
        """Inicializa a visualização base."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def clear_screen(self):
        """Limpa a tela do console."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """
        Exibe um cabeçalho formatado.
        
        Args:
            title (str): Título do cabeçalho.
        """
        width = 80
        print("=" * width)
        print(title.center(width))
        print("=" * width)
    
    def print_menu(self, options):
        """
        Exibe um menu de opções.
        
        Args:
            options (list): Lista de opções no formato (key, description).
            
        Returns:
            str: Opção selecionada pelo usuário.
        """
        for key, description in options:
            print(f"[{key}] {description}")
        
        print()
        choice = input("Escolha uma opção: ")
        return choice
    
    def print_message(self, message):
        """
        Exibe uma mensagem.
        
        Args:
            message (str): Mensagem a ser exibida.
        """
        print(message)
    
    def print_error(self, message):
        """
        Exibe uma mensagem de erro.
        
        Args:
            message (str): Mensagem de erro a ser exibida.
        """
        print(f"ERRO: {message}")
    
    def wait_for_input(self, message="Pressione ENTER para continuar..."):
        """
        Aguarda entrada do usuário.
        
        Args:
            message (str): Mensagem a ser exibida.
        """
        input(message)
    
    def get_input(self, prompt):
        """
        Obtém entrada do usuário.
        
        Args:
            prompt (str): Mensagem de solicitação.
            
        Returns:
            str: Entrada do usuário.
        """
        return input(prompt)
    
    def get_int_input(self, prompt, min_value=None, max_value=None):
        """
        Obtém um número inteiro do usuário.
        
        Args:
            prompt (str): Mensagem de solicitação.
            min_value (int): Valor mínimo permitido.
            max_value (int): Valor máximo permitido.
            
        Returns:
            int: Número inteiro fornecido pelo usuário.
        """
        while True:
            try:
                value = int(input(prompt))
                
                if min_value is not None and value < min_value:
                    print(f"O valor deve ser pelo menos {min_value}.")
                    continue
                
                if max_value is not None and value > max_value:
                    print(f"O valor deve ser no máximo {max_value}.")
                    continue
                
                return value
            except ValueError:
                print("Por favor, digite um número inteiro válido.")
    
    def get_yes_no_input(self, prompt):
        """
        Obtém uma resposta sim/não do usuário.
        
        Args:
            prompt (str): Mensagem de solicitação.
            
        Returns:
            bool: True para sim, False para não.
        """
        while True:
            response = input(f"{prompt} (s/n): ").lower()
            if response in ['s', 'sim', 'y', 'yes']:
                return True
            elif response in ['n', 'não', 'nao', 'no']:
                return False
            else:
                print("Por favor, responda com 's' ou 'n'.")
