# game/views/world_view.py
from game.views.base_view import BaseView

class WorldView(BaseView):
    """
    Visualização do mundo do jogo.
    
    Exibe o mapa e informações relacionadas.
    """
    
    def __init__(self):
        """Inicializa a visualização do mundo."""
        super().__init__()
        
        # Mapeamento de terrenos para caracteres
        self.terrain_chars = {
            'grass': '.',
            'plains': ',',
            'desert': '~',
            'tundra': '-',
            'snow': '*',
            'mountains': '^',
            'hills': 'n',
            'forest': 'f',
            'jungle': 'j',
            'marsh': 'm',
            'water': '≈',
            'ocean': '≈',
            'coast': '≈',
            'ice': '#'
        }
        
        # Mapeamento de recursos para caracteres
        self.resource_chars = {
            'iron': 'I',
            'horses': 'H',
            'coal': 'C',
            'oil': 'O',
            'aluminum': 'A',
            'uranium': 'U',
            'wheat': 'w',
            'cattle': 'c',
            'sheep': 's',
            'deer': 'd',
            'bananas': 'b',
            'fish': 'f',
            'whales': 'W',
            'pearls': 'p',
            'gold': 'g',
            'silver': '$',
            'gems': 'G',
            'marble': 'M',
            'ivory': 'i',
            'furs': 'F',
            'dyes': 'D',
            'spices': 'S',
            'silk': 'k',
            'sugar': 's',
            'cotton': 'c',
            'wine': 'w',
            'incense': 'I'
        }
        
        # Cores ANSI para diferentes elementos
        self.colors = {
            'reset': '\033[0m',
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'bg_black': '\033[40m',
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
            'bg_blue': '\033[44m',
            'bg_magenta': '\033[45m',
            'bg_cyan': '\033[46m',
            'bg_white': '\033[47m'
        }
    
    def show_map(self, world, player_civ, center_x=None, center_y=None, radius=10):
        """
        Exibe o mapa do mundo.
        
        Args:
            world: Mundo do jogo.
            player_civ: Civilização do jogador.
            center_x (int): Coordenada X central (opcional).
            center_y (int): Coordenada Y central (opcional).
            radius (int): Raio de visualização (opcional).
        """
        self.clear_screen()
        
        if not world:
            self.print_error("Mundo não inicializado")
            return
        
        # Define o centro do mapa
        if center_x is None or center_y is None:
            # Se não for especificado, usa a capital do jogador como centro
            if player_civ and player_civ.cities:
                capital = player_civ.cities[0]
                center_x, center_y = capital.x, capital.y
            else:
                center_x, center_y = world.width // 2, world.height // 2
        
        # Calcula os limites da visualização
        min_x = max(0, center_x - radius)
        max_x = min(world.width - 1, center_x + radius)
        min_y = max(0, center_y - radius)
        max_y = min(world.height - 1, center_y + radius)
        
        # Exibe o cabeçalho
        self.print_header(f"MAPA DO MUNDO - Turno {player_civ.game_state.current_turn}")
        
        # Exibe coordenadas X
        print("   ", end="")
        for x in range(min_x, max_x + 1):
            print(f"{x % 10}", end="")
        print()
        
        # Exibe o mapa
        for y in range(min_y, max_y + 1):
            # Exibe coordenada Y
            print(f"{y:2d} ", end="")
            
            for x in range(min_x, max_x + 1):
                tile = world.get_tile(x, y)
                
                if not tile:
                    print(" ", end="")
                    continue
                
                # Verifica se o tile é visível para o jogador
                is_visible = False
                for unit in player_civ.units:
                    if abs(unit.x - x) <= 2 and abs(unit.y - y) <= 2:
                        is_visible = True
                        break
                
                for city in player_civ.cities:
                    if abs(city.x - x) <= 3 and abs(city.y - y) <= 3:
                        is_visible = True
                        break
                
                if not is_visible:
                    print("?", end="")
                    continue
                
                # Determina o que exibir no tile
                char = self.terrain_chars.get(tile.terrain_type, '?')
                color = self.colors['reset']
                
                # Adiciona cor com base no terreno
                if tile.terrain_type in ['water', 'ocean', 'coast']:
                    color = self.colors['blue']
                elif tile.terrain_type in ['grass', 'plains', 'forest', 'jungle']:
                    color = self.colors['green']
                elif tile.terrain_type in ['desert']:
                    color = self.colors['yellow']
                elif tile.terrain_type in ['tundra', 'snow', 'ice']:
                    color = self.colors['white']
                elif tile.terrain_type in ['mountains', 'hills']:
                    color = self.colors['magenta']
                
                # Prioriza exibir cidades
                if tile.city:
                    char = 'C'
                    # Cor da cidade com base no dono
                    if tile.city.owner == player_civ:
                        color = self.colors['cyan']
                    else:
                        color = self.colors['red']
                
                # Prioriza exibir unidades
                elif tile.units:
                    unit = tile.units[0]  # Exibe apenas a primeira unidade
                    char = 'U'
                    # Cor da unidade com base no dono
                    if unit.owner == player_civ:
                        color = self.colors['cyan']
                    else:
                        color = self.colors['red']
                
                # Exibe recursos se não houver cidade ou unidade
                elif tile.resource and tile.resource in self.resource_chars:
                    char = self.resource_chars[tile.resource]
                
                print(f"{color}{char}{self.colors['reset']}", end="")
            
            print()
        
        print("\nLegenda:")
        print("C - Cidade, U - Unidade, ? - Área não explorada")
        print(", ".join([f"{self.terrain_chars[t]} - {t.capitalize()}" for t in self.terrain_chars]))
    
    def show_minimap(self, world, player_civ):
        """
        Exibe um minimapa do mundo.
        
        Args:
            world: Mundo do jogo.
            player_civ: Civilização do jogador.
        """
        self.clear_screen()
        
        if not world:
            self.print_error("Mundo não inicializado")
            return
        
        # Exibe o cabeçalho
        self.print_header("MINIMAPA")
        
        # Calcula o fator de escala para o minimapa
        scale_x = max(1, world.width // 40)
        scale_y = max(1, world.height // 20)
        
        # Exibe o minimapa
        for y in range(0, world.height, scale_y):
            for x in range(0, world.width, scale_x):
                # Determina o que exibir para este bloco
                char = ' '
                color = self.colors['reset']
                
                # Verifica se há cidades ou unidades do jogador neste bloco
                has_player_city = False
                has_player_unit = False
                has_enemy_city = False
                has_enemy_unit = False
                
                for dy in range(scale_y):
                    for dx in range(scale_x):
                        tile_x, tile_y = x + dx, y + dy
                        if tile_x >= world.width or tile_y >= world.height:
                            continue
                        
                        tile = world.get_tile(tile_x, tile_y)
                        if not tile:
                            continue
                        
                        # Verifica se o tile é visível para o jogador
                        is_visible = False
                        for unit in player_civ.units:
                            if abs(unit.x - tile_x) <= 2 and abs(unit.y - tile_y) <= 2:
                                is_visible = True
                                break
                        
                        for city in player_civ.cities:
                            if abs(city.x - tile_x) <= 3 and abs(city.y - tile_y) <= 3:
                                is_visible = True
                                break
                        
                        if not is_visible:
                            continue
                        
                        # Verifica se há cidades ou unidades
                        if tile.city:
                            if tile.city.owner == player_civ:
                                has_player_city = True
                            else:
                                has_enemy_city = True
                        
                        for unit in tile.units:
                            if unit.owner == player_civ:
                                has_player_unit = True
                            else:
                                has_enemy_unit = True
                
                # Prioriza o que exibir
                if has_player_city:
                    char = 'C'
                    color = self.colors['cyan']
                elif has_enemy_city:
                    char = 'C'
                    color = self.colors['red']
                elif has_player_unit:
                    char = 'U'
                    color = self.colors['cyan']
                elif has_enemy_unit:
                    char = 'U'
                    color = self.colors['red']
                else:
                    # Exibe o terreno predominante
                    terrain_counts = {}
                    for dy in range(scale_y):
                        for dx in range(scale_x):
                            tile_x, tile_y = x + dx, y + dy
                            if tile_x >= world.width or tile_y >= world.height:
                                continue
                            
                            tile = world.get_tile(tile_x, tile_y)
                            if not tile:
                                continue
                            
                            terrain = tile.terrain_type
                            terrain_counts[terrain] = terrain_counts.get(terrain, 0) + 1
                    
                    if terrain_counts:
                        # Encontra o terreno mais comum
                        predominant_terrain = max(terrain_counts.items(), key=lambda x: x[1])[0]
                        char = self.terrain_chars.get(predominant_terrain, '?')
                        
                        # Adiciona cor com base no terreno
                        if predominant_terrain in ['water', 'ocean', 'coast']:
                            color = self.colors['blue']
                        elif predominant_terrain in ['grass', 'plains', 'forest', 'jungle']:
                            color = self.colors['green']
                        elif predominant_terrain in ['desert']:
                            color = self.colors['yellow']
                        elif predominant_terrain in ['tundra', 'snow', 'ice']:
                            color = self.colors['white']
                        elif predominant_terrain in ['mountains', 'hills']:
                            color = self.colors['magenta']
                
                print(f"{color}{char}{self.colors['reset']}", end="")
            
            print()
        
        print("\nLegenda:")
        print("C - Cidade, U - Unidade")
        print("Azul - Jogador, Vermelho - Inimigo")
        
        self.wait_for_input()
    
    def show_tile_info(self, tile, player_civ):
        """
        Exibe informações detalhadas sobre um tile.
        
        Args:
            tile: Tile a ser exibido.
            player_civ: Civilização do jogador.
        """
        if not tile:
            self.print_error("Tile inválido")
            return
        
        self.clear_screen()
        self.print_header(f"INFORMAÇÕES DO TILE ({tile.x}, {tile.y})")
        
        # Exibe informações básicas
        print(f"Terreno: {tile.terrain_type.capitalize()}")
        print(f"Recurso: {tile.resource.capitalize() if tile.resource else 'Nenhum'}")
        print(f"Melhoria: {tile.improvement.capitalize() if tile.improvement else 'Nenhuma'}")
        print(f"Dono: {tile.owner.name if tile.owner else 'Nenhum'}")
        
        # Exibe informações sobre a cidade, se houver
        if tile.city:
            print("\nCIDADE:")
            print(f"Nome: {tile.city.name}")
            print(f"Dono: {tile.city.owner.name if tile.city.owner else 'Nenhum'}")
            print(f"População: {tile.city.population}")
            print(f"Saúde: {tile.city.health}/{tile.city.max_health}")
            
            if tile.city.producing:
                prod_type = tile.city.producing['type']
                prod_id = tile.city.producing['id']
                progress = tile.city.producing['progress']
                cost = tile.city.producing['cost']
                print(f"Produzindo: {prod_id} ({prod_type}) - {progress}/{cost}")
        
        # Exibe informações sobre unidades, se houver
        if tile.units:
            print("\nUNIDADES:")
            for unit in tile.units:
                print(f"Tipo: {unit.type}")
                print(f"Dono: {unit.owner.name if unit.owner else 'Nenhum'}")
                print(f"Saúde: {unit.health}/{unit.max_health}")
                print(f"Movimentos: {unit.moves_left}/{unit.movement}")
                print(f"Status: {'Fortificado' if unit.is_fortified else ('Dormindo' if unit.is_sleeping else 'Ativo')}")
                print()
        
        self.wait_for_input()
