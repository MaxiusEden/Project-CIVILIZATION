import json
import os
from typing import Dict, Any

class I18n:
    def __init__(self, base_path: str, user_path: str = None, lang: str = 'pt-BR'):
        self.lang = lang
        self.translations = self._load_translations(base_path, user_path)

    def _load_translations(self, base_path: str, user_path: str = None) -> Dict[str, Any]:
        with open(base_path, encoding='utf-8') as f:
            base = json.load(f)
        if user_path and os.path.exists(user_path):
            with open(user_path, encoding='utf-8') as f:
                user = json.load(f)
            self._deep_update(base, user)
        return base

    def _deep_update(self, d, u):
        for k, v in u.items():
            if isinstance(v, dict) and k in d:
                self._deep_update(d[k], v)
            else:
                d[k] = v

    def t(self, key: str, default: str = '') -> str:
        """Busca uma string traduzida pelo caminho 'menu.item'"""
        parts = key.split('.')
        d = self.translations.get(self.lang, {})
        for p in parts:
            if isinstance(d, dict) and p in d:
                d = d[p]
            else:
                return default or key
        return d if isinstance(d, str) else default or key

# Exemplo de uso:
# i18n = I18n('data/game_text.json', 'data/game_text.user.json', lang='en-US')
# print(i18n.t('main_menu.title'))
