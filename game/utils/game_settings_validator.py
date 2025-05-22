from typing import Dict, Any
from pydantic import BaseModel, Field, ValidationError
import json
import os

class DifficultyLevel(BaseModel):
    name: str
    ai_bonus: float
    barbarian_activity: float
    player_bonus: float
    description: str

class MapType(BaseModel):
    name: str
    description: str

class MapSize(BaseModel):
    name: str
    width: int
    height: int
    players: int
    city_states: int
    description: str

class GameSpeed(BaseModel):
    name: str
    research_speed: float
    production_speed: float
    gold_speed: float
    culture_speed: float
    growth_speed: float
    description: str

class VictoryCondition(BaseModel):
    name: str
    description: str

class GameSettings(BaseModel):
    difficulty_levels: Dict[str, DifficultyLevel]
    map_types: Dict[str, MapType]
    map_sizes: Dict[str, MapSize]
    game_speeds: Dict[str, GameSpeed]
    victory_conditions: Dict[str, VictoryCondition]


def load_and_validate_settings(settings_path: str, user_path: str = None) -> GameSettings:
    """
    Carrega e valida as configurações do jogo, mesclando com configurações do usuário se existirem.
    """
    with open(settings_path, encoding='utf-8') as f:
        base = json.load(f)
    if user_path and os.path.exists(user_path):
        with open(user_path, encoding='utf-8') as f:
            user = json.load(f)
        # Merge user over base
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d:
                    deep_update(d[k], v)
                else:
                    d[k] = v
        deep_update(base, user)
    try:
        return GameSettings(**base)
    except ValidationError as e:
        import logging
        logging.getLogger("game.utils.game_settings_validator").error(f'Erro de validação nas configurações do jogo: {e}')
        raise

# Exemplo de uso:
# settings = load_and_validate_settings('data/game_settings.json', 'data/game_settings.user.json')
# print(settings.dict())
