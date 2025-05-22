# game/utils/logger.py
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(log_level=None, log_file=None, max_bytes=2*1024*1024, backup_count=5):
    """
    Configura o sistema de logging com rotação de logs e nível configurável.
    
    Args:
        log_level (int|str|None): Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL) ou None para ler de env LOG_LEVEL.
        log_file (str): Caminho para o arquivo de log. Se None, logs vão para o console.
        max_bytes (int): Tamanho máximo do arquivo de log antes da rotação (default 2MB).
        backup_count (int): Quantidade de arquivos de backup mantidos.
        
    Returns:
        logging.Logger: Logger configurado.
    """
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level, logging.INFO)
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)
    
    logger.info(f"Logger configurado. Nível: {logging.getLevelName(log_level)} | Arquivo: {log_file or 'console'}")
    
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

# Exemplo de integração:
# from game.utils.logger import setup_logger
# logger = setup_logger(log_file='logs/game.log')
# game_logger = get_game_logger('main')
# game_logger.info('Mensagem de teste')
