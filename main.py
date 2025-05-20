#!/usr/bin/env python3
"""
Civilization - Versão em Texto
Baseado no jogo Sid Meier's Civilization

Arquivo principal do jogo.
"""

import os
import sys
import logging
import argparse
import random
import json
import pickle
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("game.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("main")

# Importa os módulos do jogo
try:
    from game.controllers.game_controller import GameController
    from game.views.menu_view import MenuView
    from game.views.game_view import GameView
except ImportError as e:
    logger.error(f"Erro ao importar módulos do jogo: {e}")
    print(f"Erro ao iniciar o jogo: {e}")
    sys.exit(1)

def parse_args():
    """Analisa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description='Civilization - Versão em Texto')
    parser.add_argument('--debug', action='store_true', help='Ativa o modo de depuração')
    parser.add_argument('--load', type=str, help='Carrega um jogo salvo')
    return parser.parse_args()

def main():
    """Função principal do jogo."""
    # Analisa argumentos da linha de comando
    args = parse_args()
    
    # Configura o nível de logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Modo de depuração ativado")
    
    # Inicializa as visualizações
    menu_view = MenuView()
    game_view = GameView()
    
    # Inicializa o controlador do jogo
    game_controller = GameController()
    
    # Carrega um jogo salvo, se especificado
    if args.load:
        if os.path.exists(f"saves/{args.load}.save"):
            try:
                game_controller.load_game(args.load)
                logger.info(f"Jogo carregado: {args.load}")
                start_game(game_controller, game_view)
            except Exception as e:
                logger.error(f"Erro ao carregar o jogo: {e}")
                print(f"Erro ao carregar o jogo: {e}")
        else:
            logger.error(f"Arquivo de salvamento não encontrado: {args.load}")
            print(f"Arquivo de salvamento não encontrado: {args.load}")
    
    # Loop principal do menu
    while True:
        choice = menu_view.show_main_menu()
        
        if choice == '0':
            # Sair
            if menu_view.confirm_exit():
                logger.info("Saindo do jogo")
                break
        
        elif choice == '1':
            # Novo Jogo
            config = menu_view.show_new_game_menu()
            if config:
                logger.info(f"Iniciando novo jogo com configuração: {config}")
                game_controller.new_game(config)
                start_game(game_controller, game_view)
        
        elif choice == '2':
            # Carregar Jogo
            saves = get_save_files()
            save_name = menu_view.show_load_game_menu(saves)
            
            if save_name:
                try:
                    game_controller.load_game(save_name)
                    logger.info(f"Jogo carregado: {save_name}")
                    start_game(game_controller, game_view)
                except Exception as e:
                    logger.error(f"Erro ao carregar o jogo: {e}")
                    menu_view.print_error(f"Erro ao carregar o jogo: {e}")
                    menu_view.wait_for_input()
        
        elif choice == '3':
            # Configurações
            settings_choice = menu_view.show_settings_menu()
            
            # Implementar alteração de configurações aqui
            # Por enquanto, apenas exibe a escolha
            if settings_choice:
                logger.debug(f"Configuração selecionada: {settings_choice}")
        
        elif choice == '4':
            # Sobre
            menu_view.show_about()

def start_game(game_controller, game_view):
    """
    Inicia o loop principal do jogo.
    
    Args:
        game_controller: Controlador do jogo.
        game_view: Visualização do jogo.
    """
    logger.info("Iniciando loop do jogo")
    
    game_state = game_controller.game_state
    player_civ = game_state.player_civ
    
    # Centro inicial do mapa
    center_x, center_y = None, None
    
    # Se o jogador tem uma capital, centraliza nela
    if player_civ.cities:
        capital = player_civ.cities[0]
        center_x, center_y = capital.x, capital.y
    
    # Loop principal do jogo
    running = True
    while running:
        # Verifica condições de vitória/derrota
        victory_status = game_controller.check_victory_conditions()
        
        if victory_status['game_over']:
            game_view.show_game_over(
                victory_status['victory'],
                player_civ,
                game_state.current_turn,
                victory_status['score']
            )
            break
        
        # Exibe a tela do jogo e obtém o comando do jogador
        command = game_view.show_game_screen(game_state, center_x, center_y)
        
        if command == 'q':
            # Sair para o menu
            if game_view.get_yes_no_input("Tem certeza que deseja sair para o menu? O progresso não salvo será perdido."):
                break
        
        elif command == 'e':
            # Encerrar turno
            game_controller.end_turn()
            logger.info(f"Turno encerrado. Novo turno: {game_state.current_turn}")
        
        elif command == 's':
            # Salvar jogo
            save_name = game_view.show_save_game_dialog()
            
            if save_name:
                try:
                    game_controller.save_game(save_name)
                    game_view.print_message(f"Jogo salvo como '{save_name}'")
                    game_view.wait_for_input()
                except Exception as e:
                    logger.error(f"Erro ao salvar o jogo: {e}")
                    game_view.print_error(f"Erro ao salvar o jogo: {e}")
                    game_view.wait_for_input()
        
        elif command == 'm':
            # Mover unidade
            unit = game_view.show_unit_list(player_civ.units)
            
            if unit:
                action = game_view.show_unit_actions(unit)
                
                if action:
                    result = game_controller.perform_unit_action(unit, action)
                    
                    if result.get('success', False):
                        game_view.print_message(result.get('message', 'Ação realizada com sucesso.'))
                    else:
                        game_view.print_error(result.get('message', 'Não foi possível realizar a ação.'))
                    
                    game_view.wait_for_input()
                    
                    # Atualiza o centro do mapa para a posição da unidade
                    center_x, center_y = unit.x, unit.y
        
        elif command == 'a':
            # Atacar
            unit = game_view.show_unit_list(player_civ.units)
            
            if unit:
                action = {'action': 'attack'}
                x = game_view.get_int_input("Coordenada X do alvo: ")
                y = game_view.get_int_input("Coordenada Y do alvo: ")
                action['x'] = x
                action['y'] = y
                
                result = game_controller.perform_unit_action(unit, action)
                
                if result.get('success', False):
                    game_view.print_message(result.get('message', 'Ataque realizado com sucesso.'))
                else:
                    game_view.print_error(result.get('message', 'Não foi possível realizar o ataque.'))
                
                game_view.wait_for_input()
        
        elif command == 'b':
            # Construir melhoria
            unit = game_view.show_unit_list([u for u in player_civ.units if hasattr(u, 'can_build') and u.can_build])
            
            if unit:
                action = game_view.show_unit_actions(unit)
                
                if action and action['action'] == 'build_improvement':
                    result = game_controller.perform_unit_action(unit, action)
                    
                    if result.get('success', False):
                        game_view.print_message(result.get('message', 'Construção iniciada com sucesso.'))
                    else:
                        game_view.print_error(result.get('message', 'Não foi possível iniciar a construção.'))
                    
                    game_view.wait_for_input()
        
        elif command == 'c':
            # Gerenciar cidade
            city = game_view.show_city_list(player_civ.cities)
            
            if city:
                action = game_view.show_city_screen(
                    city, 
                    game_controller.get_building_data(), 
                    game_controller.get_unit_data()
                )
                
                if action:
                    result = game_controller.perform_city_action(city, action)
                    
                    if result.get('success', False):
                        game_view.print_message(result.get('message', 'Ação realizada com sucesso.'))
                    else:
                        game_view.print_error(result.get('message', 'Não foi possível realizar a ação.'))
                    
                    game_view.wait_for_input()
                    
                    # Atualiza o centro do mapa para a posição da cidade
                    center_x, center_y = city.x, city.y
        
        elif command == 'u':
            # Listar unidades
            unit = game_view.show_unit_list(player_civ.units)
            
            if unit:
                # Atualiza o centro do mapa para a posição da unidade
                center_x, center_y = unit.x, unit.y
        
        elif command == 't':
            # Tecnologias
            tech_id = game_view.show_tech_screen(player_civ, game_controller.get_tech_tree())
            
            if tech_id:
                result = game_controller.research_technology(tech_id)
                
                if result.get('success', False):
                    game_view.print_message(result.get('message', 'Pesquisa iniciada com sucesso.'))
                else:
                    game_view.print_error(result.get('message', 'Não foi possível iniciar a pesquisa.'))
                
                game_view.wait_for_input()
        
        elif command == 'd':
            # Diplomacia
            action = game_view.show_diplomacy_screen(player_civ, game_state.civilizations)
            
            if action:
                result = game_controller.perform_diplomatic_action(action)
                
                if result.get('success', False):
                    game_view.print_message(result.get('message', 'Ação diplomática realizada com sucesso.'))
                else:
                    game_view.print_error(result.get('message', 'Não foi possível realizar a ação diplomática.'))
                
                game_view.wait_for_input()
        
        elif command == 'i':
            # Informações do tile
            x = game_view.get_int_input("Coordenada X: ")
            y = game_view.get_int_input("Coordenada Y: ")
            
            tile = game_state.world.get_tile(x, y)
            
            if tile:
                game_view.world_view.show_tile_info(tile, player_civ)
                
                # Atualiza o centro do mapa para a posição do tile
                center_x, center_y = x, y
            else:
                game_view.print_error("Coordenadas inválidas.")
                game_view.wait_for_input()
        
        elif command == 'v':
            # Ver minimapa
            game_view.world_view.show_minimap(game_state.world, player_civ)

def get_save_files():
    """
    Obtém a lista de arquivos de salvamento disponíveis.
    
    Returns:
        list: Lista de nomes de arquivos de salvamento.
    """
    # Cria o diretório de salvamentos se não existir
    if not os.path.exists("saves"):
        os.makedirs("saves")
    
    # Lista os arquivos de salvamento
    saves = []
    for file in os.listdir("saves"):
        if file.endswith(".save"):
            saves.append(file[:-5])  # Remove a extensão .save
    
    return saves

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Jogo encerrado pelo usuário (Ctrl+C)")
        print("\nJogo encerrado.")
    except Exception as e:
        logger.critical(f"Erro não tratado: {e}", exc_info=True)
        print(f"\nErro crítico: {e}")
        print("Consulte o arquivo de log para mais detalhes.")
