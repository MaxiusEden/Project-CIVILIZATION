"""
Visualização para a árvore tecnológica.
"""

import os
from game.views import BaseView

class TechView(BaseView):
    """
    Visualização para a árvore tecnológica.
    """
    
    def show_tech_tree(self, player_civ, tech_tree):
        """
        Exibe a árvore tecnológica.
        
        Args:
            player_civ: Civilização do jogador.
            tech_tree (dict): Dados da árvore tecnológica.
            
        Returns:
            str: ID da tecnologia selecionada para pesquisa, ou None para cancelar.
        """
        self.clear_screen()
        self.print_header("ÁRVORE TECNOLÓGICA")
        
        # Tecnologia atual em pesquisa
        current_research = player_civ.current_research
        if current_research:
            tech_id = current_research.get('id')
            progress = current_research.get('progress', 0)
            cost = current_research.get('cost', 0)
            
            tech_name = tech_tree.get(tech_id, {}).get('name', tech_id)
            
            print(f"PESQUISA ATUAL: {tech_name}")
            print(f"Progresso: {progress}/{cost}")
            
            # Calcula turnos restantes
            turns_left = (cost - progress) // player_civ.science_per_turn if player_civ.science_per_turn > 0 else "∞"
            print(f"Turnos restantes: {turns_left}")
            
            # Opção para cancelar pesquisa atual
            if self.get_yes_no_input("Deseja cancelar a pesquisa atual?"):
                return 'cancel'
            
            return None
        
        # Organiza tecnologias por era
        techs_by_era = {}
        for tech_id, tech_data in tech_tree.items():
            era = tech_data.get('era', 'ancient')
            if era not in techs_by_era:
                techs_by_era[era] = []
            techs_by_era[era].append((tech_id, tech_data))
        
        # Ordem das eras
        era_order = ['ancient', 'classical', 'medieval', 'renaissance', 'industrial', 'modern', 'atomic', 'information', 'future']
        
        # Lista de tecnologias disponíveis para pesquisa
        available_techs = []
        
        # Exibe tecnologias por era
        for era in era_order:
            if era in techs_by_era:
                print(f"\n== ERA {era.upper()} ==")
                
                for tech_id, tech_data in techs_by_era[era]:
                    name = tech_data.get('name', tech_id)
                    cost = tech_data.get('cost', 0)
                    
                    # Verifica se a tecnologia já foi pesquisada
                    if tech_id in player_civ.technologies:
                        status = "[PESQUISADA]"
                    # Verifica se a tecnologia está disponível para pesquisa
                    elif self._can_research(tech_id, tech_data, player_civ.technologies):
                        status = "[DISPONÍVEL]"
                        available_techs.append(tech_id)
                    else:
                        status = "[BLOQUEADA]"
                    
                    # Exibe requisitos
                    requires = tech_data.get('requires', [])
                    req_str = ", ".join(requires) if requires else "Nenhum"
                    
                    print(f"{tech_id}: {name} (Custo: {cost}) {status}")
                    print(f"  Requer: {req_str}")
                    
                    # Exibe o que a tecnologia desbloqueia
                    unlocks = []
                    if tech_data.get('unlocks_buildings'):
                        unlocks.append(f"Edifícios: {', '.join(tech_data['unlocks_buildings'])}")
                    if tech_data.get('unlocks_units'):
                        unlocks.append(f"Unidades: {', '.join(tech_data['unlocks_units'])}")
                    if tech_data.get('unlocks_improvements'):
                        unlocks.append(f"Melhorias: {', '.join(tech_data['unlocks_improvements'])}")
                    
                    if unlocks:
                        print(f"  Desbloqueia: {'; '.join(unlocks)}")
        
        # Se não houver tecnologias disponíveis
        if not available_techs:
            self.print_message("Não há tecnologias disponíveis para pesquisa.")
            self.wait_for_input()
            return None
        
        # Menu de seleção
        print("\nTECNOLOGIAS DISPONÍVEIS PARA PESQUISA:")
        for i, tech_id in enumerate(available_techs):
            tech_name = tech_tree.get(tech_id, {}).get('name', tech_id)
            tech_cost = tech_tree.get(tech_id, {}).get('cost', 0)
            
            # Calcula turnos estimados
            turns = tech_cost // player_civ.science_per_turn if player_civ.science_per_turn > 0 else "∞"
            
            print(f"{i+1}. {tech_name} (Custo: {tech_cost}, Turnos: {turns})")
        
        print("\n0. Voltar")
        
        choice = self.get_int_input("Selecione uma tecnologia para pesquisar (0 para voltar): ", 0, len(available_techs))
        
        if choice == 0:
            return None
        
        return available_techs[choice - 1]
    
    def _can_research(self, tech_id, tech_data, researched_techs):
        """
        Verifica se uma tecnologia pode ser pesquisada.
        
        Args:
            tech_id (str): ID da tecnologia.
            tech_data (dict): Dados da tecnologia.
            researched_techs (list): Lista de tecnologias já pesquisadas.
            
        Returns:
            bool: True se a tecnologia pode ser pesquisada, False caso contrário.
        """
        # Se já foi pesquisada, não pode pesquisar novamente
        if tech_id in researched_techs:
            return False
        
        # Verifica se todos os requisitos foram atendidos
        requires = tech_data.get('requires', [])
        if not requires:
            return True
        
        for req in requires:
            if req not in researched_techs:
                return False
        
        return True
