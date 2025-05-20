# game/views/menu_view.py
from game.views.base_view import BaseView

class MenuView(BaseView):
    """
    Visualização para menus do jogo.
    
    Exibe menus principais e de configuração.
    """
    
    def __init__(self):
        """Inicializa a visualização de menus."""
        super().__init__()
    
    def show_main_menu(self):
        """
        Exibe o menu principal.
        
        Returns:
            str: Opção selecionada pelo usuário.
        """
        self.clear_screen()
        self.print_header("CIVILIZATION - MENU PRINCIPAL")
        
        options = [
            ('1', 'Novo Jogo'),
            ('2', 'Carregar Jogo'),
            ('3', 'Configurações'),
            ('4', 'Sobre'),
            ('0', 'Sair')
        ]
        
        return self.print_menu(options)
    
    def show_new_game_menu(self):
        """
        Exibe o menu de novo jogo.
        
        Returns:
            dict: Configurações do novo jogo.
        """
        self.clear_screen()
        self.print_header("NOVO JOGO")
        
        config = {}
        
        # Seleciona a civilização
        print("Escolha sua civilização:")
        options = [
            ('1', 'Americanos'),
            ('2', 'Chineses'),
            ('3', 'Egípcios'),
            ('4', 'Ingleses'),
            ('5', 'Romanos')
        ]
        
        civ_choice = self.print_menu(options)
        civ_map = {
            '1': 'american',
            '2': 'chinese',
            '3': 'egyptian',
            '4': 'english',
            '5': 'roman'
        }
        
        config['civilization'] = civ_map.get(civ_choice, 'american')
        
        # Seleciona o tamanho do mapa
        print("\nEscolha o tamanho do mapa:")
        options = [
            ('1', 'Pequeno (32x32)'),
            ('2', 'Médio (64x64)'),
            ('3', 'Grande (96x96)'),
            ('4', 'Enorme (128x128)')
        ]
        
        size_choice = self.print_menu(options)
        size_map = {
            '1': (32, 32),
            '2': (64, 64),
            '3': (96, 96),
            '4': (128, 128)
        }
        
        config['map_size'] = size_map.get(size_choice, (64, 64))
        
        # Seleciona a dificuldade
        print("\nEscolha a dificuldade:")
        options = [
            ('1', 'Fácil'),
            ('2', 'Normal'),
            ('3', 'Difícil'),
            ('4', 'Rei'),
            ('5', 'Imperador'),
            ('6', 'Divindade')
        ]
        
        difficulty_choice = self.print_menu(options)
        difficulty_map = {
            '1': 'easy',
            '2': 'normal',
            '3': 'hard',
            '4': 'king',
            '5': 'emperor',
            '6': 'deity'
        }
        
        config['difficulty'] = difficulty_map.get(difficulty_choice, 'normal')
        
        # Seleciona o número de civilizações IA
        config['ai_civs'] = self.get_int_input("\nNúmero de civilizações IA (1-7): ", 1, 7)
        
        return config
    
    def show_load_game_menu(self, saves):
        """
        Exibe o menu de carregar jogo.
        
        Args:
            saves (list): Lista de jogos salvos disponíveis.
            
        Returns:
            str: Nome do jogo salvo selecionado, ou None para cancelar.
        """
        self.clear_screen()
        self.print_header("CARREGAR JOGO")
        
        if not saves:
            self.print_message("Nenhum jogo salvo encontrado.")
            self.wait_for_input()
            return None
        
        print("Escolha um jogo salvo:")
        
        options = [(str(i+1), save) for i, save in enumerate(saves)]
        options.append(('0', 'Voltar'))
        
        choice = self.print_menu(options)
        
        if choice == '0':
            return None
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(saves):
                return saves[index]
        except ValueError:
            pass
        
        return None
    
    def show_settings_menu(self):
        """
        Exibe o menu de configurações.
        
        Returns:
            dict: Configurações atualizadas.
        """
        self.clear_screen()
        self.print_header("CONFIGURAÇÕES")
        
        options = [
            ('1', 'Ativar/Desativar Sons'),
            ('2', 'Ativar/Desativar Música'),
            ('3', 'Ativar/Desativar Animações'),
            ('0', 'Voltar')
        ]
        
        choice = self.print_menu(options)
        
        # Aqui retornamos apenas a escolha, a lógica de alteração das configurações
        # seria implementada no controlador
        return choice
    
    def show_about(self):
        """Exibe informações sobre o jogo."""
        self.clear_screen()
        self.print_header("SOBRE")
        
        print("Civilization - Versão em Texto")
        print("Baseado no jogo Sid Meier's Civilization")
        print("\nDesenvolvido como projeto educacional")
        print("\n© 2023 - Todos os direitos reservados")
        
        self.wait_for_input()
    
    def confirm_exit(self):
        """
        Confirma se o usuário deseja sair do jogo.
        
        Returns:
            bool: True se o usuário confirmar, False caso contrário.
        """
        return self.get_yes_no_input("Tem certeza que deseja sair do jogo?")
