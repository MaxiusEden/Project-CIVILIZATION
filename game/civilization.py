#!/usr/bin/env python3
import curses
import os
import sys

def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    try:
        import curses
        return True
    except ImportError:
        print("Erro: O módulo 'curses' não está instalado.")
        print("Em sistemas Windows, instale com: pip install windows-curses")
        return False

def check_terminal_size():
    """Verifica se o terminal tem tamanho suficiente."""
    try:
        height, width = os.get_terminal_size()
        if height < 24 or width < 80:
            print(f"Erro: Terminal muito pequeno ({width}x{height}).")
            print("O jogo requer um terminal de pelo menos 80x24 caracteres.")
            return False
        return True
    except (AttributeError, OSError):
        # Se não conseguir determinar o tamanho, assume que está ok
        return True

def create_data_directories():
    """Cria diretórios necessários para os dados do jogo."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("saves", exist_ok=True)

def create_sample_data_files():
    """Cria arquivos de dados de exemplo se não existirem."""
    import json
    
    # Arquivo de tecnologias
    if not os.path.exists("data/technologies.json"):
        tech_data = {
            "agriculture": {
                "cost": 50,
                "prerequisites": [],
                "unlocks": ["farm"]
            },
            "animal_husbandry": {
                "cost": 60,
                "prerequisites": [],
                "unlocks": ["pasture"]
            },
            "mining": {
                "cost": 60,
                "prerequisites": [],
                "unlocks": ["mine"]
            },
            "pottery": {
                "cost": 50,
                "prerequisites": [],
                "unlocks": ["granary"]
            },
            "archery": {
                "cost": 70,
                "prerequisites": ["animal_husbandry"],
                "unlocks": ["archer"]
            },
            "bronze_working": {
                "cost": 80,
                "prerequisites": ["mining"],
                "unlocks": ["spearman"]
            },
            "writing": {
                "cost": 120,
                "prerequisites": ["pottery"],
                "unlocks": ["library"]
            }
        }
        
        with open("data/technologies.json", "w") as f:
            json.dump(tech_data, f, indent=4)
    
    # Arquivo de unidades
    if not os.path.exists("data/units.json"):
        units_data = {
            "settler": {
                "name": "Colonizador",
                "cost": 80,
                "maintenance": 1,
                "combat_strength": 0,
                "movement": 2,
                "abilities": ["found_city"]
            },
            "builder": {
                "name": "Construtor",
                "cost": 50,
                "maintenance": 1,
                "combat_strength": 0,
                "movement": 2,
                "abilities": ["build_improvement"]
            },
            "warrior": {
                "name": "Guerreiro",
                "cost": 40,
                "maintenance": 1,
                "combat_strength": 10,
                "movement": 2,
                "abilities": []
            },
            "archer": {
                "name": "Arqueiro",
                "cost": 60,
                "maintenance": 2,
                "combat_strength": 5,
                "ranged_strength": 15,
                "range": 2,
                "movement": 2,
                "abilities": [],
                "requires_tech": "archery"
            },
            "spearman": {
                "name": "Lanceiro",
                "cost": 50,
                "maintenance": 1,
                "combat_strength": 15,
                "movement": 2,
                "abilities": ["anti_cavalry"],
                "requires_tech": "bronze_working"
            }
        }
        
        with open("data/units.json", "w") as f:
            json.dump(units_data, f, indent=4)
    
    # Arquivo de edifícios
    if not os.path.exists("data/buildings.json"):
        buildings_data = {
            "granary": {
                "name": "Celeiro",
                "cost": 60,
                "maintenance": 1,
                "effects": {
                    "food": 2
                },
                "requires_tech": "pottery"
            },
            "monument": {
                "name": "Monumento",
                "cost": 40,
                "maintenance": 1,
                "effects": {
                    "culture": 2
                }
            },
            "library": {
                "name": "Biblioteca",
                "cost": 80,
                "maintenance": 1,
                "effects": {
                    "science": 2
                },
                "requires_tech": "writing"
            },
            "barracks": {
                "name": "Quartel",
                "cost": 70,
                "maintenance": 1,
                "effects": {
                    "unit_experience": 1
                },
                "requires_tech": "bronze_working"
            },
            "walls": {
                "name": "Muralhas",
                "cost": 100,
                "maintenance": 1,
                "effects": {
                    "defense": 5
                },
                "requires_tech": "masonry"
            },
            "market": {
                "name": "Mercado",
                "cost": 120,
                "maintenance": 1,
                "effects": {
                    "gold": 3
                },
                "requires_tech": "currency"
            },
            "water_mill": {
                "name": "Moinho d'Água",
                "cost": 100,
                "maintenance": 1,
                "effects": {
                    "food": 1,
                    "production": 1
                },
                "requires_tech": "wheel"
            }
        }
        
        with open("data/buildings.json", "w") as f:
            json.dump(buildings_data, f, indent=4)

def show_title_screen():
    """Mostra a tela de título do jogo."""
    def _title_screen(stdscr):
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Título
        title = "CIVILIZATION PYTHON"
        stdscr.addstr(height // 4, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Subtítulo
        subtitle = "Um jogo de estratégia baseado em turnos"
        stdscr.addstr(height // 4 + 2, (width - len(subtitle)) // 2, subtitle)
        
        # Menu
        menu_items = [
            "1. Novo Jogo",
            "2. Carregar Jogo (não implementado)",
            "3. Sair"
        ]
        
        for i, item in enumerate(menu_items):
            stdscr.addstr(height // 2 + i, (width - len(item)) // 2, item)
        
        # Instruções
        instructions = "Selecione uma opção (1-3)"
        stdscr.addstr(height - 3, (width - len(instructions)) // 2, instructions)
        
        stdscr.refresh()
        
        # Espera pela entrada do usuário
        while True:
            key = stdscr.getch()
            
            if key == ord('1'):
                return 1  # Novo jogo
            elif key == ord('2'):
                return 2  # Carregar jogo
            elif key == ord('3') or key == ord('q'):
                return 3  # Sair
    
    return curses.wrapper(_title_screen)

def main():
    """Função principal do jogo."""
    # Verifica dependências
    if not check_dependencies():
        return 1
    
    # Verifica tamanho do terminal
    if not check_terminal_size():
        return 1
    
    # Cria diretórios e arquivos necessários
    create_data_directories()
    create_sample_data_files()
    
    # Mostra tela de título
    choice = show_title_screen()
    
    if choice == 1:
        # Inicia novo jogo
        import main
        curses.wrapper(main.main)
    elif choice == 2:
        # Carregar jogo (não implementado)
        print("Carregar jogo não está implementado ainda.")
        return 0
    elif choice == 3:
        # Sair
        print("Obrigado por jogar!")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
