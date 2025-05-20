# game/utils/logger.py
import logging
import os
from datetime import datetime

def setup_logger(log_level=logging.INFO, log_file=None):
    """
    Configura o sistema de logging.
    
    Args:
        log_level (int): Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file (str): Caminho para o arquivo de log. Se None, logs vão para o console.
        
    Returns:
        logging.Logger: Logger configurado.
    """
    # Cria o diretório de logs se não existir e se um arquivo de log for especificado
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Configura o formato do log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configura o logger raiz
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Adiciona handler de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)
    
    # Adiciona handler de arquivo se especificado
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)
    
    return logger

def get_game_logger(name):
    """
    Obtém um logger específico para um componente do jogo.
    
    Args:
        name (str): Nome do componente.
        
    Returns:
        logging.Logger: Logger configurado.
    """
    return logging.getLogger(f"game.{name}")
