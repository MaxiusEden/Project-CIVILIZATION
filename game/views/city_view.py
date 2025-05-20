"""
Visualização para cidades no jogo.
"""

import os
from game.views import BaseView

class CityView(BaseView):
    """
    Visualização para cidades.
    """
    
    def show_city_details(self, city, buildings_data):
        """
        Exibe os detalhes de uma cidade.
        
        Args:
            city: Cidade a ser exibida.
            buildings_data (dict): Dados de edifícios.
        """
        self.clear_screen()
        self.print_header(f"CIDADE: {city.name}")
        
        # Informações básicas
        print(f"População: {city.population}")
        print(f"Saúde: {city.health}/{city.max_health}")
        print(f"Coordenadas: ({city.x}, {city.y})")
        
        # Recursos
        print("\nRECURSOS POR TURNO:")
        print(f"Comida: {city.food_per_turn}")
        print(f"Produção: {city.production_per_turn}")
        print(f"Ouro: {city.gold_per_turn}")
        print(f"Ciência: {city.science_per_turn}")
        print(f"Cultura: {city.culture_per_turn}")
        
        # Produção atual
        if city.current_production:
            prod_type = city.current_production.get('type')
            prod_id = city.current_production.get('id')
            progress = city.current_production.get('progress', 0)
            cost = city.current_production.get('cost', 0)
            
            print("\nPRODUÇÃO ATUAL:")
            if prod_type == 'building':
                building_name = buildings_data.get(prod_id, {}).get('name', prod_id)
                print(f"Edifício: {building_name}")
            elif prod_type == 'unit':
                print(f"Unidade: {prod_id}")
            
            print(f"Progresso: {progress}/{cost}")
            
            # Calcula turnos restantes
            turns_left = (cost - progress) // city.production_per_turn if city.production_per_turn > 0 else "∞"
            print(f"Turnos restantes: {turns_left}")
        else:
            print("\nNenhuma produção em andamento.")
        
        # Edifícios
        if city.buildings:
            print("\nEDIFÍCIOS:")
            for building_id in city.buildings:
                building_name = buildings_data.get(building_id, {}).get('name', building_id)
                print(f"- {building_name}")
        else:
            print("\nNenhum edifício construído.")
    
    def show_production_menu(self, city, buildings_data, units_data):
        """
        Exibe o menu de produção de uma cidade.
        
        Args:
            city: Cidade.
            buildings_data (dict): Dados de edifícios.
            units_data (dict): Dados de unidades.
            
        Returns:
            dict: Ação de produção selecionada, ou None para cancelar.
        """
        self.clear_screen()
        self.print_header(f"PRODUÇÃO: {city.name}")
        
        # Exibe produção atual
        if city.current_production:
            prod_type = city.current_production.get('type')
            prod_id = city.current_production.get('id')
            progress = city.current_production.get('progress', 0)
            cost = city.current_production.get('cost', 0)
            
            print("PRODUÇÃO ATUAL:")
            if prod_type == 'building':
                building_name = buildings_data.get(prod_id, {}).get('name', prod_id)
                print(f"Edifício: {building_name}")
            elif prod_type == 'unit':
                print(f"Unidade: {prod_id}")
            
            print(f"Progresso: {progress}/{cost}")
            
            # Calcula turnos restantes
            turns_left = (cost - progress) // city.production_per_turn if city.production_per_turn > 0 else "∞"
            print(f"Turnos restantes: {turns_left}")
            
            # Opção para cancelar produção atual
            if self.get_yes_no_input("Deseja cancelar a produção atual?"):
                return {'action': 'cancel_production'}
            
            return None
        
        # Menu de opções de produção
        print("\nO QUE DESEJA PRODUZIR?")
        options = [
            ('1', 'Edifício'),
            ('2', 'Unidade'),
            ('0', 'Voltar')
        ]
        
        choice = self.print_menu(options)
        
        if choice == '0':
            return None
        
        if choice == '1':
            # Mostrar lista de edifícios disponíveis
            available_buildings = city.get_available_buildings(buildings_data)
            
            if not available_buildings:
                self.print_message("Não há edifícios disponíveis para construção.")
                self.wait_for_input()
                return None
            
            self.clear_screen()
            self.print_header("CONSTRUIR EDIFÍCIO")
            
            print("ID | Nome | Custo | Descrição")
            print("-" * 70)
            
            for i, building_id in enumerate(available_buildings):
                building = buildings_data.get(building_id, {})
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
            available_units = city.get_available_units(units_data)
            
            if not available_units:
                self.print_message("Não há unidades disponíveis para produção.")
                self.wait_for_input()
                return None
            
            self.clear_screen()
            self.print_header("PRODUZIR UNIDADE")
            
            print("ID | Nome | Custo | Força | Movimento | Descrição")
            print("-" * 80)
            
            for i, unit_id in enumerate(available_units):
                unit = units_data.get(unit_id, {})
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
        
        return None
    
    def show_city_list(self, cities):
        """
        Exibe uma lista de cidades para seleção.
        
        Args:
            cities (list): Lista de cidades.
            
        Returns:
            City: Cidade selecionada, ou None para cancelar.
        """
        if not cities:
            self.print_message("Você não possui cidades.")
            self.wait_for_input()
            return None
        
        self.clear_screen()
        self.print_header("SUAS CIDADES")
        
        print("ID | Nome | População | Produção | Comida | Ouro | Ciência")
        print("-" * 70)
        
        for i, city in enumerate(cities):
            print(f"{i+1:2d} | {city.name:15s} | {city.population:9d} | {city.production_per_turn:9d} | "
                  f"{city.food_per_turn:6d} | {city.gold_per_turn:4d} | {city.science_per_turn:7d}")
        
        print("\n0. Voltar")
        
        choice = self.get_int_input("Selecione uma cidade (0 para voltar): ", 0, len(cities))
        
        if choice == 0:
            return None
        
        return cities[choice - 1]
    
    def show_city_screen(self, city, buildings_data, units_data):
        """
        Exibe a tela principal de uma cidade.
        
        Args:
            city: Cidade a ser exibida.
            buildings_data (dict): Dados de edifícios.
            units_data (dict): Dados de unidades.
            
        Returns:
            dict: Ação selecionada, ou None para voltar.
        """
        while True:
            self.clear_screen()
            self.print_header(f"CIDADE: {city.name}")
            
            # Informações básicas
            print(f"População: {city.population}")
            print(f"Saúde: {city.health}/{city.max_health}")
            print(f"Coordenadas: ({city.x}, {city.y})")
            
            # Recursos
            print("\nRECURSOS POR TURNO:")
            print(f"Comida: {city.food_per_turn}")
            print(f"Produção: {city.production_per_turn}")
            print(f"Ouro: {city.gold_per_turn}")
            print(f"Ciência: {city.science_per_turn}")
            print(f"Cultura: {city.culture_per_turn}")
            
            # Produção atual
            if city.current_production:
                prod_type = city.current_production.get('type')
                prod_id = city.current_production.get('id')
                progress = city.current_production.get('progress', 0)
                cost = city.current_production.get('cost', 0)
                
                print("\nPRODUÇÃO ATUAL:")
                if prod_type == 'building':
                    building_name = buildings_data.get(prod_id, {}).get('name', prod_id)
                    print(f"Edifício: {building_name}")
                elif prod_type == 'unit':
                    unit_name = units_data.get(prod_id, {}).get('name', prod_id)
                    print(f"Unidade: {unit_name}")
                
                print(f"Progresso: {progress}/{cost}")
                
                # Calcula turnos restantes
                turns_left = (cost - progress) // city.production_per_turn if city.production_per_turn > 0 else "∞"
                print(f"Turnos restantes: {turns_left}")
            else:
                print("\nNenhuma produção em andamento.")
            
            # Menu de opções
            print("\nOPÇÕES:")
            options = [
                ('1', 'Gerenciar Produção'),
                ('2', 'Gerenciar Cidadãos'),
                ('3', 'Comprar Tile'),
                ('4', 'Ver Edifícios'),
                ('0', 'Voltar')
            ]
            
            choice = self.print_menu(options)
            
            if choice == '0':
                return None
            
            elif choice == '1':
                # Gerenciar produção
                production_action = self.show_production_menu(city, buildings_data, units_data)
                if production_action:
                    return production_action
            
            elif choice == '2':
                # Gerenciar cidadãos (a ser implementado)
                self.print_message("Funcionalidade ainda não implementada.")
                self.wait_for_input()
            
            elif choice == '3':
                # Comprar tile (a ser implementado)
                self.print_message("Funcionalidade ainda não implementada.")
                self.wait_for_input()
            
            elif choice == '4':
                # Ver edifícios
                self.show_city_details(city, buildings_data)
                self.wait_for_input()
