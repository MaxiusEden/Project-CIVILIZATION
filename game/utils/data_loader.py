# game/utils/data_loader.py
import json
import os
import logging
from pathlib import Path

class DataLoader:
    """
    Classe responsável por carregar dados de arquivos JSON.
    
    Esta classe fornece métodos para carregar e validar dados
    de arquivos JSON usados pelo jogo.
    """
    
    def __init__(self, data_dir="data"):
        """
        Inicializa o carregador de dados.
        
        Args:
            data_dir (str): Diretório contendo os arquivos de dados.
        """
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cache = {}  # Cache para dados já carregados
        
    def load_json(self, filename, required_fields=None):
        """
        Carrega dados de um arquivo JSON.
        
        Args:
            filename (str): Nome do arquivo JSON (sem o diretório).
            required_fields (list): Lista de campos obrigatórios para validação.
            
        Returns:
            dict: Dados carregados do arquivo JSON.
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado.
            json.JSONDecodeError: Se o arquivo não for um JSON válido.
            ValueError: Se os dados não contiverem os campos obrigatórios.
        """
        # Verifica se os dados já estão em cache
        if filename in self.cache:
            return self.cache[filename]
            
        file_path = self.data_dir / filename
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Valida campos obrigatórios
            if required_fields:
                for item_key, item_data in data.items():
                    missing_fields = [field for field in required_fields if field not in item_data]
                    if missing_fields:
                        self.logger.warning(
                            f"Item '{item_key}' em '{filename}' está faltando campos: {missing_fields}"
                        )
            
            # Armazena em cache
            self.cache[filename] = data
            return data
            
        except FileNotFoundError:
            self.logger.error(f"Arquivo não encontrado: {file_path}")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"Arquivo JSON inválido: {file_path}")
            raise
    
    def save_json(self, filename, data):
        """
        Salva dados em um arquivo JSON.
        
        Args:
            filename (str): Nome do arquivo JSON (sem o diretório).
            data (dict): Dados a serem salvos.
            
        Returns:
            bool: True se bem-sucedido, False caso contrário.
        """
        file_path = self.data_dir / filename
        
        try:
            # Cria o diretório se não existir
            os.makedirs(file_path.parent, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            # Atualiza o cache
            self.cache[filename] = data
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar arquivo {file_path}: {e}")
            return False
    
    def get_technologies(self):
        """
        Carrega dados de tecnologias.
        
        Returns:
            dict: Dados de tecnologias.
        """
        return self.load_json("technologies.json", ["cost", "prerequisites"])
    
    def get_units(self):
        """
        Carrega dados de unidades.
        
        Returns:
            dict: Dados de unidades.
        """
        return self.load_json("units.json", ["name", "cost", "movement"])
    
    def get_buildings(self):
        """
        Carrega dados de edifícios.
        
        Returns:
            dict: Dados de edifícios.
        """
        return self.load_json("buildings.json", ["name", "cost"])
    
    def get_terrains(self):
        """
        Carrega dados de terrenos.
        
        Returns:
            dict: Dados de terrenos.
        """
        try:
            return self.load_json("terrains.json", ["name", "movement_cost"])
        except FileNotFoundError:
            # Cria um arquivo de terrenos básico se não existir
            terrains = {
                "plains": {
                    "name": "Planície",
                    "symbol": ".",
                    "color": "green",
                    "movement_cost": 1,
                    "food": 1,
                    "production": 1,
                    "gold": 0
                },
                "hills": {
                    "name": "Colinas",
                    "symbol": "^",
                    "color": "yellow",
                    "movement_cost": 2,
                    "food": 0,
                    "production": 2,
                    "gold": 0
                },
                "mountains": {
                    "name": "Montanhas",
                    "symbol": "M",
                    "color": "white",
                    "movement_cost": 999,  # Intransponível
                    "food": 0,
                    "production": 0,
                    "gold": 0
                },
                "forest": {
                    "name": "Floresta",
                    "symbol": "♣",
                    "color": "green",
                    "movement_cost": 2,
                    "food": 1,
                    "production": 1,
                    "gold": 0
                },
                "desert": {
                    "name": "Deserto",
                    "symbol": "~",
                    "color": "yellow",
                    "movement_cost": 1,
                    "food": 0,
                    "production": 0,
                    "gold": 0
                },
                "water": {
                    "name": "Água",
                    "symbol": "≈",
                    "color": "blue",
                    "movement_cost": 999,  # Intransponível para unidades terrestres
                    "food": 1,
                    "production": 0,
                    "gold": 1
                }
            }
            self.save_json("terrains.json", terrains)
            return terrains
    
    def get_resources(self):
        """
        Carrega dados de recursos.
        
        Returns:
            dict: Dados de recursos.
        """
        try:
            return self.load_json("resources.json", ["name", "yields"])
        except FileNotFoundError:
            # Cria um arquivo de recursos básico se não existir
            resources = {
                "cattle": {
                    "name": "Gado",
                    "symbol": "C",
                    "yields": {"food": 1},
                    "valid_terrains": ["plains"],
                    "requires_tech": "animal_husbandry"
                },
                "wheat": {
                    "name": "Trigo",
                    "symbol": "W",
                    "yields": {"food": 2},
                    "valid_terrains": ["plains"],
                    "requires_tech": "agriculture"
                },
                "iron": {
                    "name": "Ferro",
                    "symbol": "I",
                    "yields": {"production": 1},
                    "valid_terrains": ["plains", "hills"],
                    "requires_tech": "iron_working",
                    "strategic": True
                },
                "horses": {
                    "name": "Cavalos",
                    "symbol": "H",
                    "yields": {"production": 1},
                    "valid_terrains": ["plains"],
                    "requires_tech": "animal_husbandry",
                    "strategic": True
                },
                "stone": {
                    "name": "Pedra",
                    "symbol": "S",
                    "yields": {"production": 1},
                    "valid_terrains": ["plains", "hills"],
                    "requires_tech": "mining"
                },
                "gold_ore": {
                    "name": "Ouro",
                    "symbol": "G",
                    "yields": {"gold": 2},
                    "valid_terrains": ["hills"],
                    "requires_tech": "mining",
                    "luxury": True
                }
            }
            self.save_json("resources.json", resources)
            return resources
