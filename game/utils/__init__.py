# game/utils/__init__.py
"""
Utilitários para o jogo.
"""

import os
import json
import random
import logging
from datetime import datetime

def load_json_data(file_path):
    """
    Carrega dados de um arquivo JSON.
    
    Args:
        file_path (str): Caminho para o arquivo JSON.
        
    Returns:
        dict: Dados carregados, ou um dicionário vazio em caso de erro.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Erro ao carregar arquivo JSON {file_path}: {e}")
        return {}

def save_json_data(file_path, data):
    """
    Salva dados em um arquivo JSON.
    
    Args:
        file_path (str): Caminho para o arquivo JSON.
        data: Dados a serem salvos.
        
    Returns:
        bool: True se os dados foram salvos com sucesso, False caso contrário.
    """
    try:
        # Cria o diretório se não existir
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar arquivo JSON {file_path}: {e}")
        return False
