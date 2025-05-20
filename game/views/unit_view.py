"""
Visualização para unidades no jogo.
"""

import os
from game.views import BaseView

class UnitView(BaseView):
    """
    Visualização para unidades.
    """
    
    def show_unit_details(self, unit):
        """
        Exibe os detalhes de uma unidade.
        
        Args:
            unit: Unidade a ser exibida.
        """
        self.clear_screen()
        self.print_header(f"UNIDADE: {unit.type}")
        
        # Informações básicas
        print(f"Posição: ({unit.x}, {unit.y})")
        print(f"Saúde: {unit.health}/{unit.max_health}")
        print(f"Movimentos: {unit.moves_left}/{unit.movement}")
        
        # Atributos de combate
        if hasattr(unit, 'strength') and unit.strength > 0:
            print(f"Força: {unit.strength}")
        
        if hasattr(unit, 'ranged_strength') and unit.ranged_strength > 0:
            print(f"Força à Distância: {unit.ranged_strength}")
            print(f"Alcance: {unit.range}")
        
        # Status
        status = []
        if hasattr(unit, 'is_fortified') and unit.is_fortified:
            status.append("Fortificado")
        
        if hasattr(unit, 'is_sleeping') and unit.is_sleeping:
            status.append("Dormindo")
        
        if hasattr(unit, 'has_acted') and unit.has_acted:
            status.append("Já agiu neste turno")
        
        if status:
            print(f"Status: {', '.join(status)}")
        
        # Habilidades especiais
        abilities = []
        if hasattr(unit, 'can_found_city') and unit.can_found_city:
            abilities.append("Pode fundar cidade")
        
        if hasattr(unit, 'can_build') and unit.can_build:
            abilities.append("Pode construir melhorias")
        
        if abilities:
            print(f"Habilidades: {', '.join(abilities)}")
    
    def show_unit_list(self, units):
        """
        Exibe uma lista de unidades para seleção.
        
        Args:
            units (list): Lista de unidades.
            
        Returns:
            Unit: Unidade selecionada, ou None para cancelar.
        """
        if not units:
            self.print_message("Você não possui unidades.")
            self.wait_for_input()
            return None
        
        self.clear_screen()
        self.print_header("SUAS UNIDADES")
        
        print("ID | Tipo | Posição | Saúde | Movimentos | Status")
        print("-" * 70)
        
        for i, unit in enumerate(units):
            # Determina o status da unidade
            status = []
            if hasattr(unit, 'is_fortified') and unit.is_fortified:
                status.append("F")
            
            if hasattr(unit, 'is_sleeping') and unit.is_sleeping:
                status.append("D")
            
            if hasattr(unit, 'has_acted') and unit.has_acted:
                status.append("A")
            
            status_str = ','.join(status) if status else "-"
            
            print(f"{i+1:2d} | {unit.type:15s} | ({unit.x:2d},{unit.y:2d}) | "
                  f"{unit.health:3d}/{unit.max_health:3d} | {unit.moves_left:2d}/{unit.movement:2d} | {status_str}")
        
        print("\n0. Voltar")
        
        choice = self.get_int_input("Selecione uma unidade (0 para voltar): ", 0, len(units))
        
        if choice == 0:
            return None
        
        return units[choice - 1]
    
    def show_unit_actions(self, unit):
        """
        Exibe as ações disponíveis para uma unidade.
        
        Args:
            unit: Unidade selecionada.
            
        Returns:
            dict: Ação a ser realizada, ou None para cancelar.
        """
        self.clear_screen()
        self.print_header(f"AÇÕES DA UNIDADE: {unit.type}")
        
        # Exibe informações da unidade
        print(f"Posição: ({unit.x}, {unit.y})")
        print(f"Saúde: {unit.health}/{unit.max_health}")
        print(f"Movimentos: {unit.moves_left}/{unit.movement}")
        
        if hasattr(unit, 'strength') and unit.strength > 0:
            print(f"Força: {unit.strength}")
        
        if hasattr(unit, 'ranged_strength') and unit.ranged_strength > 0:
            print(f"Força à Distância: {unit.ranged_strength}")
            print(f"Alcance: {unit.range}")
        
        # Exibe opções disponíveis
        print("\nAÇÕES DISPONÍVEIS:")
        options = []
        
        # Só mostra opções que requerem movimento se a unidade ainda pode se mover
        if unit.moves_left > 0 and not unit.has_acted:
            options.append(('m', 'Mover'))
            
            if hasattr(unit, 'strength') and unit.strength > 0:
                options.append(('a', 'Atacar'))
            
            if hasattr(unit, 'can_found_city') and unit.can_found_city:
                options.append(('f', 'Fundar Cidade'))
            
            if hasattr(unit, 'can_build') and unit.can_build:
                options.append(('b', 'Construir Melhoria'))
        
        # Opções que não requerem movimento
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
        
        elif choice == 'f':
            # Fundar cidade
            city_name = self.get_input("Nome da cidade: ")
            
            return {
                'action': 'found_city',
                'name': city_name
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
