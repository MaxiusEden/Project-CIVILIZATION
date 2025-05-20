import curses
import textwrap

class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.init_colors()
        
    def init_colors(self):
        """Inicializa os pares de cores para o jogo."""
        curses.start_color()
        # Terrenos
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)    # planície
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)     # água
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)    # montanha
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)    # floresta
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # recurso
        
        # Entidades
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)      # cidade
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # unidade
        
        # Interface
        curses.init_pair(8, curses.COLOR_CYAN, curses.COLOR_BLACK)     # destaque
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)    # seleção
        
    def render_world(self, world, center_x=None, center_y=None):
        """Renderiza o mapa do mundo."""
        # Determina o centro da visualização
        if center_x is None or center_y is None:
            center_x = world.width // 2
            center_y = world.height // 2
        
        # Calcula os limites da visualização
        view_width = min(self.width, world.width)
        view_height = min(self.height - 5, world.height)
        
        start_x = max(0, center_x - view_width // 2)
        start_y = max(0, center_y - view_height // 2)
        
        end_x = min(world.width, start_x + view_width)
        end_y = min(world.height, start_y + view_height)
        
        # Renderiza o mapa
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x - start_x
                screen_y = y - start_y
                
                if screen_x >= self.width or screen_y >= self.height - 5:
                    continue
                
                tile = world.get_tile(x, y)
                if tile == '.':
                    self.stdscr.addch(screen_y, screen_x, '.', curses.color_pair(1))
                elif tile == '~':
                    self.stdscr.addch(screen_y, screen_x, '~', curses.color_pair(2))
                elif tile == '^':
                    self.stdscr.addch(screen_y, screen_x, '^', curses.color_pair(3))
                elif tile == '#':
                    self.stdscr.addch(screen_y, screen_x, '#', curses.color_pair(4))
                elif tile == '*':
                    self.stdscr.addch(screen_y, screen_x, '*', curses.color_pair(5))
        
        # Renderiza cidades
        for city in world.cities:
            x, y = city.position
            screen_x = x - start_x
            screen_y = y - start_y
            
            if (0 <= screen_x < self.width and 0 <= screen_y < self.height - 5):
                self.stdscr.addch(screen_y, screen_x, 'O', curses.color_pair(6) | curses.A_BOLD)
        
        # Renderiza unidades
        for unit in world.units:
            x, y = unit.position
            screen_x = x - start_x
            screen_y = y - start_y
            
            if (0 <= screen_x < self.width and 0 <= screen_y < self.height - 5):
                self.stdscr.addch(screen_y, screen_x, unit.symbol, curses.color_pair(7) | curses.A_BOLD)
    
    def render_status(self, civilization, turn):
        """Renderiza informações de status do jogador."""
        status_line = f"Turno: {turn} | {civilization.name} | Era: {civilization.era} | Ouro: {civilization.gold} | Ciência: {civilization.science}/turno"
        self.stdscr.addstr(self.height - 4, 0, status_line)
        
        # Mostra pesquisa atual
        if civilization.researching:
            research_line = f"Pesquisando: {civilization.researching.name} ({civilization.research_progress}/{civilization.researching.cost})"
            self.stdscr.addstr(self.height - 3, 0, research_line)
        
        # Mostra comandos disponíveis
        commands = "Comandos: (n)ext turn, (c)ity menu, (t)ech tree, (u)nit commands, (d)iplomacy, (q)uit"
        self.stdscr.addstr(self.height - 2, 0, commands)

    def city_menu(self, civilization):
        """Mostra o menu de gerenciamento de cidades."""
        # Limpa a tela
        self.stdscr.clear()
        
        # Mostra lista de cidades
        self.stdscr.addstr(0, 0, "=== GERENCIAMENTO DE CIDADES ===", curses.A_BOLD)
        
        if not civilization.cities:
            self.stdscr.addstr(2, 0, "Você não possui nenhuma cidade.")
            self.stdscr.addstr(4, 0, "Pressione qualquer tecla para voltar...")
            self.stdscr.refresh()
            self.stdscr.getch()
            return
        
        # Lista todas as cidades
        for i, city in enumerate(civilization.cities):
            city_info = f"{i+1}. {city.name} (Pop: {city.population})"
            self.stdscr.addstr(i+2, 0, city_info)
        
        self.stdscr.addstr(len(civilization.cities) + 3, 0, "Selecione uma cidade (número) ou pressione 'q' para voltar: ")
        self.stdscr.refresh()
        
        # Espera pela entrada do usuário
        while True:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
                
            # Verifica se o usuário selecionou uma cidade válida
            try:
                city_index = int(chr(key)) - 1
                if 0 <= city_index < len(civilization.cities):
                    self.city_detail_menu(civilization.cities[city_index])
                    break
            except (ValueError, IndexError):
                pass
    
    def city_detail_menu(self, city):
        """Mostra detalhes de uma cidade específica e opções de gerenciamento."""
        while True:
            # Limpa a tela
            self.stdscr.clear()
            
            # Mostra informações da cidade
            self.stdscr.addstr(0, 0, f"=== {city.name} ===", curses.A_BOLD)
            self.stdscr.addstr(2, 0, f"População: {city.population}")
            self.stdscr.addstr(3, 0, f"Comida: {city.food}/{city.population * 10} (+{city.food_per_turn}/turno)")
            self.stdscr.addstr(4, 0, f"Produção: {city.production} (+{city.production_per_turn}/turno)")
            self.stdscr.addstr(5, 0, f"Ouro: +{city.gold_per_turn}/turno")
            self.stdscr.addstr(6, 0, f"Ciência: +{city.science_per_turn}/turno")
            self.stdscr.addstr(7, 0, f"Cultura: +{city.culture_per_turn}/turno")
            
            # Mostra edifícios
            self.stdscr.addstr(9, 0, "Edifícios:")
            if not city.buildings:
                self.stdscr.addstr(10, 2, "Nenhum edifício construído.")
            else:
                for i, building in enumerate(city.buildings):
                    self.stdscr.addstr(10 + i, 2, f"- {building.name}")
            
            # Mostra fila de produção
            production_y = 11 + (len(city.buildings) if city.buildings else 1)
            self.stdscr.addstr(production_y, 0, "Produção Atual:")
            
            if city.building_queue:
                building = city.building_queue[0]
                self.stdscr.addstr(production_y + 1, 2, f"Construindo: {building.name} ({city.production}/{building.cost})")
            elif city.unit_queue:
                unit_type = city.unit_queue[0]
                self.stdscr.addstr(production_y + 1, 2, f"Produzindo: {unit_type.capitalize()} ({city.production}/{city._get_unit_cost(unit_type)})")
            else:
                self.stdscr.addstr(production_y + 1, 2, "Nada em produção.")
            
            # Mostra opções
            options_y = production_y + 3
            self.stdscr.addstr(options_y, 0, "Opções:")
            self.stdscr.addstr(options_y + 1, 2, "b - Construir edifício")
            self.stdscr.addstr(options_y + 2, 2, "u - Produzir unidade")
            self.stdscr.addstr(options_y + 3, 2, "q - Voltar")
            
            self.stdscr.refresh()
            
            # Processa entrada do usuário
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
            elif key == ord('b'):
                self.building_menu(city)
            elif key == ord('u'):
                self.unit_production_menu(city)
    
    def building_menu(self, city):
        """Menu para escolher um edifício para construir."""
        # Limpa a tela
        self.stdscr.clear()
        
        # Obtém edifícios disponíveis
        available_buildings = self._get_available_buildings(city)
        
        if not available_buildings:
            self.stdscr.addstr(0, 0, "Nenhum edifício disponível para construção.")
            self.stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar...")
            self.stdscr.refresh()
            self.stdscr.getch()
            return
        
        # Mostra edifícios disponíveis
        self.stdscr.addstr(0, 0, "=== CONSTRUIR EDIFÍCIO ===", curses.A_BOLD)
        
        for i, building in enumerate(available_buildings):
            building_info = f"{i+1}. {building.name} (Custo: {building.cost})"
            self.stdscr.addstr(i+2, 0, building_info)
            
            # Mostra descrição do edifício
            wrapped_desc = textwrap.wrap(building.description, self.width - 4)
            for j, line in enumerate(wrapped_desc):
                self.stdscr.addstr(i+2, 40 + j, line)
        
        self.stdscr.addstr(len(available_buildings) + 3, 0, "Selecione um edifício (número) ou pressione 'q' para voltar: ")
        self.stdscr.refresh()
        
        # Espera pela entrada do usuário
        while True:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
                
            # Verifica se o usuário selecionou um edifício válido
            try:
                building_index = int(chr(key)) - 1
                if 0 <= building_index < len(available_buildings):
                    city.queue_building(available_buildings[building_index].building_type)
                    return
            except (ValueError, IndexError):
                pass
    
    def _get_available_buildings(self, city):
        """Retorna uma lista de edifícios disponíveis para construção."""
        from game.building import Building
        
        # Lista de tipos de edifícios básicos
        building_types = ["granary", "monument", "library", "barracks", "walls", "market", "water_mill"]
        
        available = []
        for building_type in building_types:
            building = Building(building_type)
            if building.can_be_built(city, city.civilization.technologies):
                available.append(building)
                
        return available
    
    def unit_production_menu(self, city):
        """Menu para escolher uma unidade para produzir."""
        # Limpa a tela
        self.stdscr.clear()
        
        # Obtém unidades disponíveis
        available_units = self._get_available_units(city)
        
        if not available_units:
            self.stdscr.addstr(0, 0, "Nenhuma unidade disponível para produção.")
            self.stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar...")
            self.stdscr.refresh()
            self.stdscr.getch()
            return
        
        # Mostra unidades disponíveis
        self.stdscr.addstr(0, 0, "=== PRODUZIR UNIDADE ===", curses.A_BOLD)
        
        for i, (unit_type, data) in enumerate(available_units.items()):
            unit_info = f"{i+1}. {data['name']} (Custo: {data['cost']})"
            self.stdscr.addstr(i+2, 0, unit_info)
            
            # Mostra descrição da unidade
            if 'description' in data:
                wrapped_desc = textwrap.wrap(data['description'], self.width - 4)
                for j, line in enumerate(wrapped_desc):
                    if i+2+j < self.height - 1:  # Evita escrever fora da tela
                        self.stdscr.addstr(i+2, 40 + j, line)
        
        self.stdscr.addstr(len(available_units) + 3, 0, "Selecione uma unidade (número) ou pressione 'q' para voltar: ")
        self.stdscr.refresh()
        
        # Espera pela entrada do usuário
        while True:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
                
            # Verifica se o usuário selecionou uma unidade válida
            try:
                unit_index = int(chr(key)) - 1
                if 0 <= unit_index < len(available_units):
                    unit_type = list(available_units.keys())[unit_index]
                    city.queue_unit(unit_type)
                    return
            except (ValueError, IndexError):
                pass
    
    def _get_available_units(self, city):
        """Retorna um dicionário de unidades disponíveis para produção."""
        import json
        
        try:
            with open('data/units.json', 'r') as f:
                units_data = json.load(f)
                
            # Filtra unidades com base nas tecnologias disponíveis
            available_units = {}
            for unit_type, data in units_data.items():
                required_tech = data.get('requires_tech')
                if required_tech is None or city.civilization.has_technology(required_tech):
                    available_units[unit_type] = data
                    
            return available_units
        except (FileNotFoundError, json.JSONDecodeError):
            # Retorna unidades básicas se o arquivo não for encontrado
            return {
                "settler": {"name": "Colonizador", "cost": 80},
                "warrior": {"name": "Guerreiro", "cost": 40},
                "builder": {"name": "Construtor", "cost": 50}
            }
    
    def tech_tree(self, civilization):
        """Mostra a árvore tecnológica e permite escolher uma tecnologia para pesquisar."""
        while True:
            # Limpa a tela
            self.stdscr.clear()
            
            # Mostra tecnologias pesquisadas
            self.stdscr.addstr(0, 0, "=== ÁRVORE TECNOLÓGICA ===", curses.A_BOLD)
            self.stdscr.addstr(2, 0, "Tecnologias Pesquisadas:")
            
            if not civilization.technologies:
                self.stdscr.addstr(3, 2, "Nenhuma tecnologia pesquisada.")
                tech_y_offset = 4
            else:
                for i, tech in enumerate(civilization.technologies):
                    self.stdscr.addstr(i+3, 2, f"- {tech.name}")
                tech_y_offset = len(civilization.technologies) + 4
            
            # Mostra pesquisa atual
            if civilization.researching:
                self.stdscr.addstr(tech_y_offset, 0, f"Pesquisando: {civilization.researching.name} ({civilization.research_progress}/{civilization.researching.cost})")
                tech_y_offset += 2
            else:
                self.stdscr.addstr(tech_y_offset, 0, "Nenhuma pesquisa em andamento.")
                tech_y_offset += 2
            
            # Mostra tecnologias disponíveis
            available_techs = civilization.get_available_technologies()
            
            if not available_techs:
                self.stdscr.addstr(tech_y_offset, 0, "Nenhuma tecnologia disponível para pesquisa.")
            else:
                self.stdscr.addstr(tech_y_offset, 0, "Tecnologias Disponíveis:")
                for i, tech in enumerate(available_techs):
                    tech_info = f"{i+1}. {tech.name} (Custo: {tech.cost})"
                    self.stdscr.addstr(tech_y_offset + i + 1, 2, tech_info)
            
            self.stdscr.addstr(self.height - 2, 0, "Selecione uma tecnologia (número) ou pressione 'q' para voltar: ")
            self.stdscr.refresh()
            
            # Espera pela entrada do usuário
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
                
            # Verifica se o usuário selecionou uma tecnologia válida
            try:
                tech_index = int(chr(key)) - 1
                if 0 <= tech_index < len(available_techs):
                    tech = available_techs[tech_index]
                    civilization.start_research(tech.name)
                    return
            except (ValueError, IndexError):
                pass
    
    def unit_command_menu(self, civilization):
        """Menu para selecionar e comandar unidades."""
        # Limpa a tela
        self.stdscr.clear()
        
        # Mostra lista de unidades
        self.stdscr.addstr(0, 0, "=== COMANDAR UNIDADES ===", curses.A_BOLD)
        
        if not civilization.units:
            self.stdscr.addstr(2, 0, "Você não possui nenhuma unidade.")
            self.stdscr.addstr(4, 0, "Pressione qualquer tecla para voltar...")
            self.stdscr.refresh()
            self.stdscr.getch()
            return
        
        # Lista todas as unidades
        for i, unit in enumerate(civilization.units):
                        unit_info = f"{i+1}. {unit.name} ({unit.position[0]}, {unit.position[1]}) - Movimentos: {unit.moves_left}/{unit.max_moves}"
                        self.stdscr.addstr(i+2, 0, unit_info)
        
        self.stdscr.addstr(len(civilization.units) + 3, 0, "Selecione uma unidade (número) ou pressione 'q' para voltar: ")
        self.stdscr.refresh()
        
        # Espera pela entrada do usuário
        while True:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
                
            # Verifica se o usuário selecionou uma unidade válida
            try:
                unit_index = int(chr(key)) - 1
                if 0 <= unit_index < len(civilization.units):
                    self.unit_action_menu(civilization.units[unit_index])
                    break
            except (ValueError, IndexError):
                pass
    
    def unit_action_menu(self, unit):
        """Menu para escolher ações para uma unidade específica."""
        while True:
            # Limpa a tela
            self.stdscr.clear()
            
            # Mostra informações da unidade
            self.stdscr.addstr(0, 0, f"=== {unit.name} ===", curses.A_BOLD)
            self.stdscr.addstr(2, 0, f"Posição: ({unit.position[0]}, {unit.position[1]})")
            self.stdscr.addstr(3, 0, f"Saúde: {unit.health}/100")
            self.stdscr.addstr(4, 0, f"Movimentos: {unit.moves_left}/{unit.max_moves}")
            
            if hasattr(unit, 'combat_strength'):
                self.stdscr.addstr(5, 0, f"Força de Combate: {unit.combat_strength}")
            
            if hasattr(unit, 'ranged_strength') and unit.ranged_strength > 0:
                self.stdscr.addstr(6, 0, f"Força à Distância: {unit.ranged_strength}")
                self.stdscr.addstr(7, 0, f"Alcance: {unit.range}")
            
            # Mostra habilidades
            abilities_y = 8
            self.stdscr.addstr(abilities_y, 0, "Habilidades:")
            if not unit.abilities:
                self.stdscr.addstr(abilities_y + 1, 2, "Nenhuma habilidade especial.")
            else:
                for i, ability in enumerate(unit.abilities):
                    self.stdscr.addstr(abilities_y + i + 1, 2, f"- {ability}")
            
            # Mostra opções
            options_y = abilities_y + (len(unit.abilities) if unit.abilities else 1) + 2
            self.stdscr.addstr(options_y, 0, "Ações:")
            
            # Opções básicas
            self.stdscr.addstr(options_y + 1, 2, "m - Mover")
            
            # Opções específicas por tipo de unidade
            action_offset = 2
            if 'found_city' in unit.abilities:
                self.stdscr.addstr(options_y + action_offset, 2, "f - Fundar cidade")
                action_offset += 1
                
            if 'build_improvement' in unit.abilities:
                self.stdscr.addstr(options_y + action_offset, 2, "b - Construir melhoria")
                action_offset += 1
            
            if unit.combat_strength > 0:
                self.stdscr.addstr(options_y + action_offset, 2, "a - Atacar")
                action_offset += 1
            
            self.stdscr.addstr(options_y + action_offset, 2, "q - Voltar")
            
            self.stdscr.refresh()
            
            # Processa entrada do usuário
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
            elif key == ord('m'):
                self.move_unit(unit)
            elif key == ord('f') and 'found_city' in unit.abilities:
                unit.found_city()
                return
            elif key == ord('b') and 'build_improvement' in unit.abilities:
                self.build_improvement_menu(unit)
            elif key == ord('a') and unit.combat_strength > 0:
                self.attack_menu(unit)
    
    def move_unit(self, unit):
        """Interface para mover uma unidade."""
        # Limpa a tela
        self.stdscr.clear()
        
        # Mostra instruções
        self.stdscr.addstr(0, 0, "=== MOVER UNIDADE ===", curses.A_BOLD)
        self.stdscr.addstr(2, 0, f"Unidade: {unit.name}")
        self.stdscr.addstr(3, 0, f"Posição atual: ({unit.position[0]}, {unit.position[1]})")
        self.stdscr.addstr(4, 0, f"Movimentos restantes: {unit.moves_left}")
        
        self.stdscr.addstr(6, 0, "Use as setas para mover a unidade:")
        self.stdscr.addstr(7, 2, "↑ - Norte")
        self.stdscr.addstr(8, 2, "↓ - Sul")
        self.stdscr.addstr(9, 2, "← - Oeste")
        self.stdscr.addstr(10, 2, "→ - Leste")
        self.stdscr.addstr(12, 0, "Pressione 'q' para voltar.")
        
        self.stdscr.refresh()
        
        # Processa entrada do usuário
        while unit.moves_left > 0:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
            elif key == curses.KEY_UP:
                unit.move(0, -1)
            elif key == curses.KEY_DOWN:
                unit.move(0, 1)
            elif key == curses.KEY_LEFT:
                unit.move(-1, 0)
            elif key == curses.KEY_RIGHT:
                unit.move(1, 0)
            
            # Atualiza informações após o movimento
            self.stdscr.addstr(3, 0, f"Posição atual: ({unit.position[0]}, {unit.position[1]})    ")
            self.stdscr.addstr(4, 0, f"Movimentos restantes: {unit.moves_left}    ")
            self.stdscr.refresh()
            
            if unit.moves_left <= 0:
                self.stdscr.addstr(14, 0, "Sem movimentos restantes. Pressione qualquer tecla para continuar...")
                self.stdscr.refresh()
                self.stdscr.getch()
                return
    
    def build_improvement_menu(self, unit):
        """Menu para escolher uma melhoria para construir."""
        # Limpa a tela
        self.stdscr.clear()
        
        # Lista de melhorias disponíveis
        improvements = [
            ("farm", "Fazenda", "Aumenta a produção de alimentos."),
            ("mine", "Mina", "Aumenta a produção."),
            ("pasture", "Pasto", "Melhora recursos de gado."),
            ("plantation", "Plantação", "Melhora recursos de luxo."),
            ("camp", "Acampamento", "Melhora recursos de caça.")
        ]
        
        # Mostra melhorias disponíveis
        self.stdscr.addstr(0, 0, "=== CONSTRUIR MELHORIA ===", curses.A_BOLD)
        
        for i, (imp_id, name, desc) in enumerate(improvements):
            self.stdscr.addstr(i+2, 0, f"{i+1}. {name} - {desc}")
        
        self.stdscr.addstr(len(improvements) + 3, 0, "Selecione uma melhoria (número) ou pressione 'q' para voltar: ")
        self.stdscr.refresh()
        
        # Espera pela entrada do usuário
        while True:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
                
            # Verifica se o usuário selecionou uma melhoria válida
            try:
                imp_index = int(chr(key)) - 1
                if 0 <= imp_index < len(improvements):
                    imp_id = improvements[imp_index][0]
                    unit.build_improvement(imp_id)
                    return
            except (ValueError, IndexError):
                pass
    
    def attack_menu(self, unit):
        """Menu para escolher um alvo para atacar."""
        # Limpa a tela
        self.stdscr.clear()
        
        # Encontra alvos possíveis
        targets = self._find_attack_targets(unit)
        
        if not targets:
            self.stdscr.addstr(0, 0, "Nenhum alvo disponível para ataque.")
            self.stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar...")
            self.stdscr.refresh()
            self.stdscr.getch()
            return
        
        # Mostra alvos disponíveis
        self.stdscr.addstr(0, 0, "=== ATACAR ===", curses.A_BOLD)
        
        for i, target in enumerate(targets):
            target_info = f"{i+1}. {target.name} ({target.position[0]}, {target.position[1]}) - Saúde: {target.health}/100"
            self.stdscr.addstr(i+2, 0, target_info)
        
        self.stdscr.addstr(len(targets) + 3, 0, "Selecione um alvo (número) ou pressione 'q' para voltar: ")
        self.stdscr.refresh()
        
        # Espera pela entrada do usuário
        while True:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
                
            # Verifica se o usuário selecionou um alvo válido
            try:
                target_index = int(chr(key)) - 1
                if 0 <= target_index < len(targets):
                    target = targets[target_index]
                    success = unit.attack(target)
                    
                    if success:
                        self.stdscr.addstr(len(targets) + 5, 0, f"Ataque bem-sucedido! Dano causado: {unit.combat_strength * (unit.health / 100):.1f}")
                    else:
                        self.stdscr.addstr(len(targets) + 5, 0, "Ataque falhou! Alvo fora de alcance ou sem movimentos restantes.")
                        
                    self.stdscr.addstr(len(targets) + 6, 0, "Pressione qualquer tecla para continuar...")
                    self.stdscr.refresh()
                    self.stdscr.getch()
                    return
            except (ValueError, IndexError):
                pass
    
    def _find_attack_targets(self, unit):
        """Encontra alvos possíveis para ataque."""
        targets = []
        
        # Determina o alcance de ataque
        attack_range = unit.range if hasattr(unit, 'range') and unit.range > 0 else 1
        
        # Verifica todas as unidades no mundo
        for target in unit.civilization.world.units:
            # Ignora unidades da mesma civilização
            if target.civilization == unit.civilization:
                continue
                
            # Calcula a distância
            tx, ty = target.position
            ux, uy = unit.position
            distance = max(abs(tx - ux), abs(ty - uy))
            
            # Verifica se está ao alcance
            if distance <= attack_range:
                targets.append(target)
        
        return targets
    
    def diplomacy_menu(self, civilization):
        """Menu para gerenciar relações diplomáticas."""
        # Limpa a tela
        self.stdscr.clear()
        
        # Obtém outras civilizações
        other_civs = [civ for civ in civilization.world.civilizations if civ != civilization]
        
        if not other_civs:
            self.stdscr.addstr(0, 0, "Não há outras civilizações conhecidas.")
            self.stdscr.addstr(2, 0, "Pressione qualquer tecla para voltar...")
            self.stdscr.refresh()
            self.stdscr.getch()
            return
        
        # Mostra lista de civilizações
        self.stdscr.addstr(0, 0, "=== DIPLOMACIA ===", curses.A_BOLD)
        
        for i, civ in enumerate(other_civs):
            # Obtém status diplomático
            status = civilization.world.diplomacy.get_status(civilization, civ)
            civ_info = f"{i+1}. {civ.name} ({civ.leader}) - Status: {status}"
            self.stdscr.addstr(i+2, 0, civ_info)
        
        self.stdscr.addstr(len(other_civs) + 3, 0, "Selecione uma civilização (número) ou pressione 'q' para voltar: ")
        self.stdscr.refresh()
        
        # Espera pela entrada do usuário
        while True:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
                
            # Verifica se o usuário selecionou uma civilização válida
            try:
                civ_index = int(chr(key)) - 1
                if 0 <= civ_index < len(other_civs):
                    self.diplomacy_action_menu(civilization, other_civs[civ_index])
                    break
            except (ValueError, IndexError):
                pass
    
    def diplomacy_action_menu(self, player_civ, target_civ):
        """Menu para escolher ações diplomáticas com uma civilização específica."""
        # Limpa a tela
        self.stdscr.clear()
        
        # Obtém status diplomático atual
        status = player_civ.world.diplomacy.get_status(player_civ, target_civ)
        
        # Mostra informações
        self.stdscr.addstr(0, 0, f"=== DIPLOMACIA COM {target_civ.name} ===", curses.A_BOLD)
        self.stdscr.addstr(2, 0, f"Líder: {target_civ.leader}")
        self.stdscr.addstr(3, 0, f"Status atual: {status}")
        
        # Mostra opções
        self.stdscr.addstr(5, 0, "Ações disponíveis:")
        
        if status == "Guerra":
            self.stdscr.addstr(6, 2, "p - Propor paz")
        else:
            self.stdscr.addstr(6, 2, "g - Declarar guerra")
            self.stdscr.addstr(7, 2, "t - Propor acordo comercial")
            self.stdscr.addstr(8, 2, "a - Propor aliança")
        
        self.stdscr.addstr(10, 2, "q - Voltar")
        
        self.stdscr.refresh()
        
        # Processa entrada do usuário
        while True:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                return
            elif key == ord('g') and status != "Guerra":
                player_civ.declare_war(target_civ)
                self.stdscr.addstr(12, 0, f"Você declarou guerra a {target_civ.name}!")
                self.stdscr.addstr(13, 0, "Pressione qualquer tecla para continuar...")
                self.stdscr.refresh()
                self.stdscr.getch()
                return
            elif key == ord('p') and status == "Guerra":
                player_civ.make_peace(target_civ)
                self.stdscr.addstr(12, 0, f"Você fez paz com {target_civ.name}!")
                self.stdscr.addstr(13, 0, "Pressione qualquer tecla para continuar...")
                self.stdscr.refresh()
                self.stdscr.getch()
                return
            elif key == ord('t') and status != "Guerra":
                self.stdscr.addstr(12, 0, f"{target_civ.name} aceitou seu acordo comercial!")
                self.stdscr.addstr(13, 0, "Pressione qualquer tecla para continuar...")
                self.stdscr.refresh()
                self.stdscr.getch()
                return
            elif key == ord('a') and status != "Guerra":
                self.stdscr.addstr(12, 0, f"{target_civ.name} aceitou sua proposta de aliança!")
                self.stdscr.addstr(13, 0, "Pressione qualquer tecla para continuar...")
                self.stdscr.refresh()
                self.stdscr.getch()
                return


    