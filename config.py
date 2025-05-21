"""
Módulo de configuração do jogo.
Gerencia o carregamento, validação e acesso às configurações do jogo.
"""
import os
import json
import logging
from typing import Dict, Any, Optional

# Configurações padrão
DEFAULT_CONFIG = {
    # Display settings
    "WINDOW_TITLE": "Project CIVILIZATION",
    "WINDOW_WIDTH": 1280,
    "WINDOW_HEIGHT": 720,
    "FULLSCREEN": False,

    # Graphics settings
    "ENABLE_3D": True,
    "RENDER_QUALITY": "Medium",  # Low, Medium, High
    "ANIMATION_SPEED": 1.0,
    "VSYNC": True,

    # Camera settings
    "CAMERA_START_HEIGHT": 10,
    "CAMERA_MIN_HEIGHT": 2,
    "CAMERA_MAX_HEIGHT": 20,
    "CAMERA_ROTATION_SPEED": 1.0,
    "CAMERA_ZOOM_SPEED": 0.5,

    # UI settings
    "UI_SCALE": 1.0,
    "FONT_SIZE": 12,
    "SHOW_TOOLTIPS": True,
    "TOOLTIP_DELAY": 0.5,  # seconds

    # Sound settings
    "ENABLE_SOUND": True,
    "MUSIC_VOLUME": 0.7,
    "SFX_VOLUME": 0.8,
}

# Validação de configurações
CONFIG_VALIDATORS = {
    "WINDOW_WIDTH": lambda x: isinstance(x, int) and 800 <= x <= 3840,
    "WINDOW_HEIGHT": lambda x: isinstance(x, int) and 600 <= x <= 2160,
    "FULLSCREEN": lambda x: isinstance(x, bool),
    "ENABLE_3D": lambda x: isinstance(x, bool),
    "RENDER_QUALITY": lambda x: x in ["Low", "Medium", "High"],
    "ANIMATION_SPEED": lambda x: isinstance(x, (int, float)) and 0.1 <= x <= 2.0,
    "VSYNC": lambda x: isinstance(x, bool),
    "CAMERA_START_HEIGHT": lambda x: isinstance(x, (int, float)) and 1 <= x <= 30,
    "CAMERA_MIN_HEIGHT": lambda x: isinstance(x, (int, float)) and 1 <= x <= 10,
    "CAMERA_MAX_HEIGHT": lambda x: isinstance(x, (int, float)) and 5 <= x <= 50,
    "CAMERA_ROTATION_SPEED": lambda x: isinstance(x, (int, float)) and 0.1 <= x <= 5.0,
    "CAMERA_ZOOM_SPEED": lambda x: isinstance(x, (int, float)) and 0.1 <= x <= 5.0,
    "UI_SCALE": lambda x: isinstance(x, (int, float)) and 0.5 <= x <= 2.0,
    "FONT_SIZE": lambda x: isinstance(x, int) and 8 <= x <= 24,
    "SHOW_TOOLTIPS": lambda x: isinstance(x, bool),
    "TOOLTIP_DELAY": lambda x: isinstance(x, (int, float)) and 0.0 <= x <= 2.0,
    "ENABLE_SOUND": lambda x: isinstance(x, bool),
    "MUSIC_VOLUME": lambda x: isinstance(x, (int, float)) and 0.0 <= x <= 1.0,
    "SFX_VOLUME": lambda x: isinstance(x, (int, float)) and 0.0 <= x <= 1.0,
}

class ConfigManager:
    """Gerencia as configurações do jogo."""
    
    def __init__(self, config_file: str = "data/user_config.json"):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file: Caminho para o arquivo de configuração do usuário
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
        
    def load_config(self) -> None:
        """Carrega as configurações do arquivo de configuração do usuário."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Atualiza as configurações com os valores do usuário
                for key, value in user_config.items():
                    if key in self.config:
                        # Valida o valor antes de atualizar
                        if self._validate_config_value(key, value):
                            self.config[key] = value
                        else:
                            self.logger.warning(f"Valor inválido para {key}: {value}. Usando valor padrão.")
                    else:
                        self.logger.warning(f"Configuração desconhecida: {key}")
                
                self.logger.info("Configurações do usuário carregadas com sucesso.")
            else:
                self.logger.info("Arquivo de configuração do usuário não encontrado. Usando configurações padrão.")
                # Cria o arquivo de configuração com valores padrão
                self.save_config()
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            self.logger.info("Usando configurações padrão.")
    
    def save_config(self) -> None:
        """Salva as configurações atuais no arquivo de configuração do usuário."""
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            self.logger.info("Configurações salvas com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém o valor de uma configuração.
        
        Args:
            key: Nome da configuração
            default: Valor padrão caso a configuração não exista
            
        Returns:
            Valor da configuração ou o valor padrão
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Define o valor de uma configuração.
        
        Args:
            key: Nome da configuração
            value: Novo valor
            
        Returns:
            True se a configuração foi atualizada com sucesso, False caso contrário
        """
        if key in self.config and self._validate_config_value(key, value):
            self.config[key] = value
            return True
        return False
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Atualiza múltiplas configurações de uma vez.
        
        Args:
            config_dict: Dicionário com as configurações a serem atualizadas
        """
        for key, value in config_dict.items():
            self.set(key, value)
    
    def _validate_config_value(self, key: str, value: Any) -> bool:
        """
        Valida o valor de uma configuração.
        
        Args:
            key: Nome da configuração
            value: Valor a ser validado
            
        Returns:
            True se o valor é válido, False caso contrário
        """
        if key in CONFIG_VALIDATORS:
            try:
                return CONFIG_VALIDATORS[key](value)
            except Exception:
                return False
        return True  # Se não houver validador, aceita qualquer valor

# Cria uma instância global do gerenciador de configurações
_config_manager = ConfigManager()

# Para compatibilidade com o código existente, exporta as configurações como variáveis globais
for key, value in _config_manager.config.items():
    globals()[key] = value

# Funções para acessar e modificar configurações
def get_config(key: str, default: Any = None) -> Any:
    """Obtém o valor de uma configuração."""
    return _config_manager.get(key, default)

def set_config(key: str, value: Any) -> bool:
    """Define o valor de uma configuração e atualiza a variável global correspondente."""
    result = _config_manager.set(key, value)
    if result:
        globals()[key] = value
    return result

def save_config() -> None:
    """Salva as configurações atuais no arquivo de configuração."""
    _config_manager.save_config()

def reload_config() -> None:
    """Recarrega as configurações do arquivo de configuração."""
    _config_manager.load_config()
    # Atualiza as variáveis globais
    for key, value in _config_manager.config.items():
        globals()[key] = value
