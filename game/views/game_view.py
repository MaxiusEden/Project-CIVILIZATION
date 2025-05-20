# game/views/game_view.py
from game.views.base_view import BaseView
from game.views.world_view import WorldView

class GameView(BaseView):
    """
    Visualização principal do jogo.
    
    Exibe a interface do jogo durante a partida.
    """
    
    def __init__(self):
        """Inicializa a visualização do jogo."""
        super().__init__()
        self.world_view = WorldView()
    
    def show_game_screen(self, game_state, center_x=None, center_y=None):
        """
        Exibe a tela principal do jogo.
        
        Args:
            game_state: Estado atual do jogo.
            center_x (int): Coordenada X central (opcional).
            center_y (int): Coordenada Y central (opcional).
            
        Returns:
            str: Comando do jogador.
        """
        self.clear_screen()
        
        if not game_state:
            self.print_error("Jogo não inicializado")
            return None
        
        player_civ = game_state.player_civ
        
        # Exibe o mapa
        self.world_view.show_map(game_state.world, player_civ, center_x, center_y)
        
        # Exibe informações do jogador
        print("\nINFORMAÇÕES DO JOGADOR:")
        print(f"Civilização: {player_civ.name}")
        print(f"Líder: {player_civ.leader_name}")
        print(f"Turno: {game_state.current_turn}")
        print(f"Ouro: {player_civ.gold}")
        print(f"Ciência: {player_civ.science}")
        print(f"Cultura: {player_civ.culture}")
        print(f"Felicidade: {player_civ.happiness}")
        
        # Exibe pesquisa atual
        if player_civ.researching:
            tech_id = player_civ.researching['tech_id']
            progress = player_civ.researching['progress']
            cost = player_civ.researching['cost']
            print(f"Pesquisando: {tech_id} - {progress}/{cost}")
        
        # Exibe menu de comandos
        print("\nCOMANDOS:")
        options = [
            ('m', 'Mover Unidade'),
            ('a', 'Atacar'),
            ('b', 'Construir Melhoria'),
            ('c', 'Gerenciar Cidade'),
            ('u', 'Listar Unidades'),
            ('t', 'Tecnologias'),
            ('d', 'Diplomacia'),
            ('i', 'Informações do Tile'),
            ('v', 'Ver Minimapa'),
            ('s', 'Salvar Jogo'),
            ('e', 'Encerrar Turno'),
            ('q', 'Sair para o Menu')
        ]
        
        for key, description in options:
            print(f"[{key}] {description}")
        
        print()
        return input("Comando: ").lower()
    
    def show_unit_list(self, units):
        """
        Exibe a lista de unidades do jogador.
        
        Args:
            units (list): Lista de unidades.
            
        Returns:
            Unit: Unidade selecionada, ou None se nenhuma for selecionada.
        """
        self.clear_screen()
        self.print_header("LISTA DE UNIDADES")
        
        if not units:
            self.print_message("Você não tem unidades.")
            self.wait_for_input()
            return None
        
        print("ID | Tipo | Posição | Saúde | Movimentos | Status")
        print("-" * 60)
        
        for i, unit in enumerate(units):
            status = 'Fortificado' if unit.is_fortified else ('Dormindo' if unit.is_sleeping else 'Ativo')
            print(f"{i+1:2d} | {unit.type:10s} | ({unit.x:2d},{unit.y:2d}) | {unit.health:3d}/{unit.max_health:3d} | {unit.moves_left:2d}/{unit.movement:2d} | {status}")
        
        print("\n0. Voltar")
        
        choice = self.get_int_input("Selecione uma unidade (0 para voltar): ", 0, len(units))
        
        if choice == 0:
            return None
        
        return units[choice - 1]
    
    def show_city_list(self, cities):
        """
        Exibe a lista de cidades do jogador.
        
        Args:
            cities (list): Lista de cidades.
            
        Returns:
            City: Cidade selecionada, ou None se nenhuma for selecionada.
        """
        self.clear_screen()
        self.print_header("LISTA DE CIDADES")
        
        if not cities:
            self.print_message("Você não tem cidades.")
            self.wait_for_input()
            return None
        
        print("ID | Nome | Posição | População | Saúde | Produzindo")
        print("-" * 70)
        
        for i, city in enumerate(cities):
            producing = "Nada"
            if city.producing:
                prod_id = city.producing['id']
                progress = city.producing['progress']
                cost = city.producing['cost']
                producing = f"{prod_id} ({progress}/{cost})"
            
            print(f"{i+1:2d} | {city.name:15s} | ({city.x:2d},{city.y:2d}) | {city.population:3d} | {city.health:3d}/{city.max_health:3d} | {producing}")
        
        print("\n0. Voltar")
        
        choice = self.get_int_input("Selecione uma cidade (0 para voltar): ", 0, len(cities))
        
        if choice == 0:
            return None
        
        return cities[choice - 1]
    
    def show_city_screen(self, city, building_data, unit_data):
        """
        Exibe a tela de gerenciamento de cidade.
        
        Args:
            city: Cidade a ser gerenciada.
            building_data (dict): Dados dos edifícios.
            unit_data (dict): Dados das unidades.
            
        Returns:
            dict: Ação a ser realizada.
        """
        self.clear_screen()
        
        if not city:
            self.print_error("Cidade inválida")
            return None
        
        self.print_header(f"CIDADE: {city.name}")
        
        # Exibe informações básicas
        print(f"População: {city.population}")
        print(f"Saúde: {city.health}/{city.max_health}")
        print(f"Comida: {city.food}/{city.food_needed} (Crescimento em {(city.food_needed - city.food) // city.food_per_turn} turnos)")
        print(f"Produção: {city.production} por turno")
        
        # Exibe produção atual
        if city.producing:
            prod_type = city.producing['type']
            prod_id = city.producing['id']
            progress = city.producing['progress']
            cost = city.producing['cost']
            turns_left = (cost - progress) // city.production if city.production > 0 else "∞"
            
            print(f"\nProduzindo: {prod_id} ({prod_type})")
            print(f"Progresso: {progress}/{cost} ({turns_left} turnos restantes)")
        else:
            print("\nNão está produzindo nada")
        
        # Exibe edifícios
        print("\nEDIFÍCIOS:")
        if city.buildings:
            for building in city.buildings:
                building_info = building_data.get(building, {})
                print(f"- {building}: {building_info.get('description', '')}")
        else:
            print("Nenhum edifício construído")
        
        # Exibe menu de opções
        print("\nOPÇÕES:")
        options = [
            ('1', 'Produzir Edifício'),
            ('2', 'Produzir Unidade'),
            ('3', 'Comprar com Ouro'),
            ('4', 'Gerenciar Tiles'),
            ('0', 'Voltar')
        ]
        
        choice = self.print_menu(options)
        
        if choice == '0':
            return None
        
        if choice == '1':
            # Mostrar lista de edifícios disponíveis
            available_buildings = city.get_available_buildings(building_data)
            
            if not available_buildings:
                self.print_message("Não há edifícios disponíveis para construção.")
                self.wait_for_input()
                return None
            
            self.clear_screen()
            self.print_header("CONSTRUIR EDIFÍCIO")
            
            print("ID | Nome | Custo | Descrição")
            print("-" * 70)
            
            for i, building_id in enumerate(available_buildings):
                building = building_data.get(building_id, {})
                name = building.get('name', building_id)
                cost = building.get('cost', 0)
                description = building.get('description', '')
                
                print(f"{i+1:2d} | {name:15s} | {cost:4d} | {description}")
            
            print("\n0. Voltar")
            
            building_choice = self.get_int_input("Selecione um edifício (0 para voltar): ", 0, len(available_buildings))
            
            if building_choice == 0:
                return None
            
            return {
                'action': 'produce_building',
                'building_id': available_buildings[building_choice - 1]
            }
        
        elif choice == '2':
            # Mostrar lista de unidades disponíveis
            available_units = city.get_available_units(unit_data)
            
            if not available_units:
                self.print_message("Não há unidades disponíveis para produção.")
                self.wait_for_input()
                return None
            
            self.clear_screen()
            self.print_header("PRODUZIR UNIDADE")
            
            print("ID | Nome | Custo | Força | Movimento | Descrição")
            print("-" * 80)
            
            for i, unit_id in enumerate(available_units):
                unit = unit_data.get(unit_id, {})
                name = unit.get('name', unit_id)
                cost = unit.get('cost', 0)
                strength = unit.get('strength', 0)
                movement = unit.get('movement', 0)
                description = unit.get('description', '')
                
                print(f"{i+1:2d} | {name:15s} | {cost:4d} | {strength:5d} | {movement:8d} | {description}")
            
            print("\n0. Voltar")
            
            unit_choice = self.get_int_input("Selecione uma unidade (0 para voltar): ", 0, len(available_units))
            
            if unit_choice == 0:
                return None
            
            return {
                'action': 'produce_unit',
                'unit_id': available_units[unit_choice - 1]
            }
        
        elif choice == '3':
            # Comprar com ouro
            self.clear_screen()
            self.print_header("COMPRAR COM OURO")
            
            options = [
                ('1', 'Comprar Edifício'),
                ('2', 'Comprar Unidade'),
                ('0', 'Voltar')
            ]
            
            buy_choice = self.print_menu(options)
            
            if buy_choice == '0':
                return None
            
            if buy_choice == '1':
                # Mostrar lista de edifícios disponíveis para compra
                available_buildings = city.get_available_buildings(building_data)
                
                if not available_buildings:
                    self.print_message("Não há edifícios disponíveis para compra.")
                    self.wait_for_input()
                    return None
                
                self.clear_screen()
                self.print_header("COMPRAR EDIFÍCIO")
                
                print("ID | Nome | Custo (Ouro) | Descrição")
                print("-" * 70)
                
                for i, building_id in enumerate(available_buildings):
                    building = building_data.get(building_id, {})
                    name = building.get('name', building_id)
                    cost = building.get('cost', 0) * 2  # Custo em ouro é dobrado
                    description = building.get('description', '')
                    
                    print(f"{i+1:2d} | {name:15s} | {cost:12d} | {description}")
                
                print("\n0. Voltar")
                
                building_choice = self.get_int_input("Selecione um edifício (0 para voltar): ", 0, len(available_buildings))
                
                if building_choice == 0:
                    return None
                
                return {
                    'action': 'buy_building',
                    'building_id': available_buildings[building_choice - 1]
                }
            
            elif buy_choice == '2':
                # Mostrar lista de unidades disponíveis para compra
                available_units = city.get_available_units(unit_data)
                
                if not available_units:
                    self.print_message("Não há unidades disponíveis para compra.")
                    self.wait_for_input()
                    return None
                
                self.clear_screen()
                self.print_header("COMPRAR UNIDADE")
                
                print("ID | Nome | Custo (Ouro) | Força | Movimento | Descrição")
                print("-" * 80)
                
                for i, unit_id in enumerate(available_units):
                    unit = unit_data.get(unit_id, {})
                    name = unit.get('name', unit_id)
                    cost = unit.get('cost', 0) * 2  # Custo em ouro é dobrado
                    strength = unit.get('strength', 0)
                    movement = unit.get('movement', 0)
                    description = unit.get('description', '')
                    
                    print(f"{i+1:2d} | {name:15s} | {cost:12d} | {strength:5d} | {movement:8d} | {description}")
                
                print("\n0. Voltar")
                
                unit_choice = self.get_int_input("Selecione uma unidade (0 para voltar): ", 0, len(available_units))
                
                if unit_choice == 0:
                    return None
                
                return {
                    'action': 'buy_unit',
                    'unit_id': available_units[unit_choice - 1]
                }
        
        elif choice == '4':
            # Gerenciar tiles
            self.clear_screen()
            self.print_header("GERENCIAR TILES")
            
            # Exibe os tiles trabalhados
            print("Tiles trabalhados:")
            if city.worked_tiles:
                for i, tile in enumerate(city.worked_tiles):
                    print(f"{i+1}. ({tile.x}, {tile.y}) - {tile.terrain_type.capitalize()}")
            else:
                print("Nenhum tile sendo trabalhado.")
            
            print("\nOpções:")
            options = [
                ('1', 'Adicionar Tile'),
                ('2', 'Remover Tile'),
                ('0', 'Voltar')
            ]
            
            tile_choice = self.print_menu(options)
            
            if tile_choice == '0':
                return None
            
            if tile_choice == '1':
                # Adicionar tile
                x = self.get_int_input("Coordenada X: ")
                y = self.get_int_input("Coordenada Y: ")
                
                return {
                    'action': 'add_worked_tile',
                    'x': x,
                    'y': y
                }
            
            elif tile_choice == '2':
                # Remover tile
                if not city.worked_tiles:
                    self.print_message("Não há tiles para remover.")
                    self.wait_for_input()
                    return None
                
                tile_index = self.get_int_input("Índice do tile a remover: ", 1, len(city.worked_tiles))
                
                return {
                    'action': 'remove_worked_tile',
                    'index': tile_index - 1
                }
        
        return None
    
    def show_tech_screen(self, player_civ, tech_tree):
        """
        Exibe a tela de tecnologias.
        
        Args:
            player_civ: Civilização do jogador.
            tech_tree (dict): Árvore de tecnologias.
            
        Returns:
            str: ID da tecnologia selecionada, ou None para voltar.
        """
        self.clear_screen()
        self.print_header("TECNOLOGIAS")
        
        # Exibe tecnologias já pesquisadas
        print("TECNOLOGIAS PESQUISADAS:")
        if player_civ.technologies:
            for tech_id in player_civ.technologies:
                tech = tech_tree.get(tech_id, {})
                print(f"- {tech.get('name', tech_id)}: {tech.get('description', '')}")
        else:
            print("Nenhuma tecnologia pesquisada.")
        
        # Exibe pesquisa atual
        if player_civ.researching:
            tech_id = player_civ.researching['tech_id']
            progress = player_civ.researching['progress']
            cost = player_civ.researching['cost']
            tech = tech_tree.get(tech_id, {})
            
            print("\nPESQUISANDO:")
            print(f"{tech.get('name', tech_id)}: {progress}/{cost}")
            print(f"Descrição: {tech.get('description', '')}")
            
            # Calcula turnos restantes
            turns_left = (cost - progress) // player_civ.science if player_civ.science > 0 else "∞"
            print(f"Turnos restantes: {turns_left}")
        
        # Exibe tecnologias disponíveis
        available_techs = []
        for tech_id, tech_data in tech_tree.items():
            # Ignora tecnologias já pesquisadas
            if tech_id in player_civ.technologies:
                continue
            
            # Verifica se já está pesquisando
            if player_civ.researching and player_civ.researching['tech_id'] == tech_id:
                continue
            
            # Verifica pré-requisitos
            prerequisites = tech_data.get('requires', [])
            all_prereqs_met = True
            
            for prereq in prerequisites:
                if prereq not in player_civ.technologies:
                    all_prereqs_met = False
                    break
            
            if all_prereqs_met:
                available_techs.append(tech_id)
        
        if available_techs:
            print("\nTECNOLOGIAS DISPONÍVEIS:")
            print("ID | Nome | Custo | Pré-requisitos | Descrição")
            print("-" * 80)
            
            for i, tech_id in enumerate(available_techs):
                tech = tech_tree.get(tech_id, {})
                name = tech.get('name', tech_id)
                cost = tech.get('cost', 0)
                prereqs = ", ".join(tech.get('requires', []))
                description = tech.get('description', '')
                
                print(f"{i+1:2d} | {name:15s} | {cost:4d} | {prereqs:15s} | {description}")
            
            print("\n0. Voltar")
            
            tech_choice = self.get_int_input("Selecione uma tecnologia para pesquisar (0 para voltar): ", 0, len(available_techs))
            
            if tech_choice == 0:
                return None
            
            return available_techs[tech_choice - 1]
        else:
            if player_civ.researching:
                self.print_message("Não há outras tecnologias disponíveis para pesquisa no momento.")
            else:
                self.print_message("Não há tecnologias disponíveis para pesquisa.")
            
            self.wait_for_input()
            return None
    
    def show_diplomacy_screen(self, player_civ, civilizations):
        """
        Exibe a tela de diplomacia.
        
        Args:
            player_civ: Civilização do jogador.
            civilizations (list): Lista de civilizações.
            
        Returns:
            dict: Ação diplomática a ser realizada.
        """
        self.clear_screen()
        self.print_header("DIPLOMACIA")
        
        # Filtra civilizações que não são do jogador
        other_civs = [civ for civ in civilizations if civ.id != player_civ.id]
        
        if not other_civs:
            self.print_message("Não há outras civilizações conhecidas.")
            self.wait_for_input()
            return None
        
        # Exibe relações com outras civilizações
        print("RELAÇÕES DIPLOMÁTICAS:")
        print("ID | Civilização | Líder | Relação")
        print("-" * 60)
        
        for i, civ in enumerate(other_civs):
            relation = player_civ.relations.get(civ.id, 'neutral')
            print(f"{i+1:2d} | {civ.name:15s} | {civ.leader_name:15s} | {relation.capitalize()}")
        
        print("\n0. Voltar")
        
        civ_choice = self.get_int_input("Selecione uma civilização (0 para voltar): ", 0, len(other_civs))
        
        if civ_choice == 0:
            return None
        
        target_civ = other_civs[civ_choice - 1]
        relation = player_civ.relations.get(target_civ.id, 'neutral')
        
        # Exibe opções diplomáticas
        self.clear_screen()
        self.print_header(f"DIPLOMACIA COM {target_civ.name}")
        
        print(f"Líder: {target_civ.leader_name}")
        print(f"Relação atual: {relation.capitalize()}")
        
        options = []
        
        if relation == 'war':
            options.append(('1', 'Propor Paz'))
        else:
            options.append(('1', 'Declarar Guerra'))
        
        options.append(('2', 'Propor Acordo Comercial'))
        options.append(('3', 'Propor Aliança Defensiva'))
        options.append(('4', 'Enviar Presente (Ouro)'))
        options.append(('0', 'Voltar'))
        
        action_choice = self.print_menu(options)
        
        if action_choice == '0':
            return None
        
        if action_choice == '1':
            if relation == 'war':
                return {
                    'action': 'make_peace',
                    'target_civ': target_civ.id
                }
            else:
                # Confirmar declaração de guerra
                if self.get_yes_no_input(f"Tem certeza que deseja declarar guerra a {target_civ.name}?"):
                    return {
                        'action': 'declare_war',
                        'target_civ': target_civ.id
                    }
                else:
                    return None
        
        elif action_choice == '2':
            # Propor acordo comercial
            return {
                'action': 'propose_trade',
                'target_civ': target_civ.id
            }
        
        elif action_choice == '3':
            # Propor aliança defensiva
            return {
                'action': 'propose_alliance',
                'target_civ': target_civ.id
            }
        
        elif action_choice == '4':
            # Enviar presente
            amount = self.get_int_input(f"Quantidade de ouro a enviar para {target_civ.name}: ", 1, player_civ.gold)
            
            return {
                'action': 'send_gift',
                'target_civ': target_civ.id,
                'amount': amount
            }
        
        return None
    
    def show_unit_actions(self, unit):
        """
        Exibe as ações disponíveis para uma unidade.
        
        Args:
            unit: Unidade selecionada.
            
        Returns:
            dict: Ação a ser realizada.
        """
        self.clear_screen()
        
        if not unit:
            self.print_error("Unidade inválida")
            return None
        
        self.print_header(f"AÇÕES DA UNIDADE: {unit.type}")
        
        # Exibe informações da unidade
        print(f"Posição: ({unit.x}, {unit.y})")
        print(f"Saúde: {unit.health}/{unit.max_health}")
        print(f"Movimentos: {unit.moves_left}/{unit.movement}")
        print(f"Força: {unit.strength}")
        if unit.ranged_strength > 0:
            print(f"Força à Distância: {unit.ranged_strength} (Alcance: {unit.range})")
        
        status = []
        if unit.is_fortified:
            status.append("Fortificado")
        if unit.is_sleeping:
            status.append("Dormindo")
        if unit.has_acted:
            status.append("Já agiu neste turno")
        
        if status:
            print(f"Status: {', '.join(status)}")
        
        # Exibe opções disponíveis
        print("\nAÇÕES DISPONÍVEIS:")
        options = []
        
        if unit.moves_left > 0 and not unit.has_acted:
            options.append(('m', 'Mover'))
            
            if unit.strength > 0 or unit.ranged_strength > 0:
                options.append(('a', 'Atacar'))
            
            if hasattr(unit, 'can_build') and unit.can_build:
                options.append(('b', 'Construir Melhoria'))
            
            if hasattr(unit, 'can_found_city') and unit.can_found_city:
                options.append(('f', 'Fundar Cidade'))
        
        if not unit.is_fortified and not unit.has_acted:
            options.append(('d', 'Fortificar'))
        
        if not unit.is_sleeping:
            options.append(('s', 'Dormir'))
        else:
            options.append(('w', 'Acordar'))
        
        options.append(('c', 'Cancelar'))
        
        choice = self.print_menu(options)
        
        if choice == 'c':
            return None
        
        if choice == 'm':
            # Mover unidade
            x = self.get_int_input("Coordenada X de destino: ")
            y = self.get_int_input("Coordenada Y de destino: ")
            
            return {
                'action': 'move',
                'x': x,
                'y': y
            }
        
        elif choice == 'a':
            # Atacar
            x = self.get_int_input("Coordenada X do alvo: ")
            y = self.get_int_input("Coordenada Y do alvo: ")
            
            return {
                'action': 'attack',
                'x': x,
                'y': y
            }
        
        elif choice == 'b':
            # Construir melhoria
            self.clear_screen()
            self.print_header("CONSTRUIR MELHORIA")
            
            # Lista de melhorias disponíveis
            improvements = [
                'farm',
                'mine',
                'trading_post',
                'lumber_mill',
                'pasture',
                'plantation',
                'quarry',
                'camp',
                'oil_well',
                'fishing_boats'
            ]
            
            print("Escolha uma melhoria para construir:")
            for i, improvement in enumerate(improvements):
                print(f"{i+1}. {improvement.replace('_', ' ').title()}")
            
            print("\n0. Cancelar")
            
            imp_choice = self.get_int_input("Selecione uma melhoria (0 para cancelar): ", 0, len(improvements))
            
            if imp_choice == 0:
                return None
            
            return {
                'action': 'build_improvement',
                'improvement': improvements[imp_choice - 1]
            }
        
        elif choice == 'f':
            # Fundar cidade
            city_name = self.get_input("Nome da cidade: ")
            
            return {
                'action': 'found_city',
                'name': city_name
            }
        
        elif choice == 'd':
            # Fortificar
            return {
                'action': 'fortify'
            }
        
        elif choice == 's':
            # Dormir
            return {
                'action': 'sleep'
            }
        
        elif choice == 'w':
            # Acordar
            return {
                'action': 'wake'
            }
        
        return None
    
    def show_save_game_dialog(self):
        """
        Exibe o diálogo para salvar o jogo.
        
        Returns:
            str: Nome do arquivo de salvamento, ou None para cancelar.
        """
        self.clear_screen()
        self.print_header("SALVAR JOGO")
        
        save_name = self.get_input("Nome do salvamento (ou 'cancelar' para voltar): ")
        
        if save_name.lower() == 'cancelar':
            return None
        
        return save_name
    
    def show_game_over(self, victory, player_civ, turn, score):
        """
        Exibe a tela de fim de jogo.
        
        Args:
            victory (bool): True se o jogador venceu, False se perdeu.
            player_civ: Civilização do jogador.
            turn (int): Turno em que o jogo terminou.
            score (int): Pontuação final.
        """
        self.clear_screen()
        
        if victory:
            self.print_header("VITÓRIA!")
            print(f"Parabéns! Sua civilização {player_civ.name} alcançou a vitória!")
        else:
            self.print_header("DERROTA")
            print(f"Sua civilização {player_civ.name} foi derrotada.")
        
        print(f"\nTurno: {turn}")
        print(f"Pontuação final: {score}")
        
        print("\nEstatísticas:")
        print(f"Cidades: {len(player_civ.cities)}")
        print(f"Unidades: {len(player_civ.units)}")
        print(f"Tecnologias: {len(player_civ.technologies)}")
        print(f"Ouro acumulado: {player_civ.gold}")
        
        self.wait_for_input("Pressione ENTER para voltar ao menu principal...")
