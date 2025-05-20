import curses
import time
import random
from game.models.world import World
from game.models.civilization import Civilization
from game.renderer import Renderer
from game.models.diplomacy import Diplomacy

def main(stdscr):
    # Configuração inicial do curses
    curses.curs_set(0)  # Esconde o cursor
    stdscr.clear()
    
    # Cria o mundo
    world = World(width=40, height=20)
    world.generate()
    
    # Cria a diplomacia
    diplomacy = Diplomacy()
    world.diplomacy = diplomacy
    
    # Cria civilizações
    player_civ = Civilization("Roma", "César")
    ai_civ1 = Civilization("Grécia", "Péricles")
    ai_civ2 = Civilization("Egito", "Cleópatra")
    
    # Adiciona civilizações ao mundo
    world.civilizations = [player_civ, ai_civ1, ai_civ2]
    player_civ.world = world
    ai_civ1.world = world
    ai_civ2.world = world
    
    # Inicializa relações diplomáticas
    diplomacy.initialize_relations(world.civilizations)
    
    # Cria unidades iniciais
    player_settler = player_civ.create_unit("settler", (random.randint(5, 15), random.randint(5, 10)))
    player_warrior = player_civ.create_unit("warrior", (player_settler.position[0] + 1, player_settler.position[1]))
    
    ai_civ1.create_unit("settler", (random.randint(25, 35), random.randint(5, 10)))
    ai_civ2.create_unit("settler", (random.randint(15, 25), random.randint(10, 15)))
    
    # Cria o renderizador
    renderer = Renderer(stdscr)
    
    # Variáveis de jogo
    turn = 1
    game_running = True
    
    # Loop principal do jogo
    while game_running:
        # Renderiza o mundo
        stdscr.clear()
        renderer.render_world(world, player_settler.position[0], player_settler.position[1])
        renderer.render_status(player_civ, turn)
        stdscr.refresh()
        
        # Processa entrada do jogador
        key = stdscr.getch()
        
        if key == ord('q'):
            # Confirma saída
            stdscr.addstr(renderer.height - 1, 0, "Tem certeza que deseja sair? (s/n)")
            confirm = stdscr.getch()
            if confirm == ord('s'):
                game_running = False
                continue
        
        elif key == ord('n'):
            # Próximo turno
            # Processa turno para todas as civilizações
            for civ in world.civilizations:
                civ.process_turn()
                for city in civ.cities:
                    city.process_turn()
                for unit in civ.units:
                    unit.process_turn()
            
            # Processa diplomacia
            diplomacy.process_turn()
            
            turn += 1
        
        elif key == ord('c'):
            # Menu de cidades
            renderer.city_menu(player_civ)
        
        elif key == ord('t'):
            # Árvore tecnológica
            renderer.tech_tree(player_civ)
        
        elif key == ord('u'):
            # Comandos de unidades
            renderer.unit_command_menu(player_civ)
        
        elif key == ord('d'):
            # Diplomacia
            renderer.diplomacy_menu(player_civ)
    
    # Mensagem de encerramento
    stdscr.clear()
    stdscr.addstr(renderer.height // 2, renderer.width // 2 - 10, "Obrigado por jogar!")
    stdscr.refresh()
    time.sleep(2)

if __name__ == "__main__":
    curses.wrapper(main)
