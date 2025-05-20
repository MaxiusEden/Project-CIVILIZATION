"""
Configurações globais para o jogo Civilization em modo texto.
"""

# Configurações de exibição
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 24

# Configurações de jogo
DEFAULT_MAP_WIDTH = 60
DEFAULT_MAP_HEIGHT = 40
DEFAULT_DIFFICULTY = 'normal'  # 'easy', 'normal', 'hard'
DEFAULT_GAME_SPEED = 'normal'  # 'quick', 'normal', 'epic'

# Configurações de civilizações
MAX_CIVILIZATIONS = 8
DEFAULT_PLAYER_CIV = 'rome'

# Configurações de geração de mundo
TERRAIN_DISTRIBUTION = {
    'water': 0.3,    # 30% de água
    'plains': 0.25,  # 25% de planícies
    'grass': 0.2,    # 20% de grama
    'hills': 0.1,    # 10% de colinas
    'mountains': 0.05,  # 5% de montanhas
    'desert': 0.05,  # 5% de deserto
    'tundra': 0.05   # 5% de tundra
}

RESOURCE_RARITY = {
    'common': 0.15,   # 15% de chance para recursos comuns
    'strategic': 0.08,  # 8% de chance para recursos estratégicos
    'luxury': 0.05    # 5% de chance para recursos de luxo
}

# Configurações de economia
BASE_GOLD_PER_TURN = 2
BASE_SCIENCE_PER_TURN = 1
BASE_CULTURE_PER_TURN = 1
BASE_FOOD_PER_TURN = 2
BASE_PRODUCTION_PER_TURN = 2

# Configurações de unidades
UNIT_MOVEMENT_COST = {
    'plains': 1,
    'grass': 1,
    'hills': 2,
    'mountains': 999,  # Intransponível para a maioria das unidades
    'water': 999,      # Intransponível para unidades terrestres
    'desert': 1,
    'tundra': 1
}

# Configurações de combate
COMBAT_STRENGTH_MULTIPLIER = 1.0
DEFENSE_BONUS = {
    'plains': 0,
    'grass': 0,
    'hills': 25,      # +25% de defesa
    'mountains': 50,  # +50% de defesa
    'water': 0,
    'desert': 0,
    'tundra': 0
}

# Configurações de diplomacia
DIPLOMACY_RELATION_LEVELS = [
    'war',           # Em guerra
    'unfriendly',    # Hostil
    'neutral',       # Neutro
    'friendly',      # Amigável
    'allied'         # Aliado
]

# Configurações de salvamento
SAVE_DIRECTORY = 'saves'
SAVE_EXTENSION = '.save'

# Configurações de log
LOG_DIRECTORY = 'logs'
LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

# Cores para o terminal
COLORS = {
    'reset': '\033[0m',
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bold': '\033[1m',
    'underline': '\033[4m'
}

# Desativar cores em sistemas que não suportam ANSI
import os
if os.name == 'nt':  # Windows
    try:
        import colorama
        colorama.init()
    except ImportError:
        # Se colorama não estiver disponível, desativa as cores
        for key in COLORS:
            COLORS[key] = ''
