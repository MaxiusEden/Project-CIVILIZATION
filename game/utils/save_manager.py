# game/utils/save_manager.py
import json
import os
import logging
from datetime import datetime
import hashlib
import threading
import time
from game.utils.logger import get_game_logger

class SaveManager:
    """
    Gerencia o salvamento e carregamento de jogos.
    
    Esta classe fornece métodos para salvar o estado do jogo em arquivos
    e carregá-los posteriormente.
    """
    
    def __init__(self, save_dir="saves"):
        """
        Inicializa o gerenciador de salvamentos.
        
        Args:
            save_dir (str): Diretório para salvar os jogos.
        """
        self.save_dir = save_dir
        self.logger = get_game_logger(self.__class__.__name__)
        
        # Cria o diretório de salvamentos se não existir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def _compute_hash(self, data: dict) -> str:
        """Gera um hash SHA256 do conteúdo serializado."""
        json_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
        return hashlib.sha256(json_bytes).hexdigest()

    def save_game(self, game_state, save_name=None) -> str | None:
        """
        Salva o estado atual do jogo.
        
        Args:
            game_state (dict): Estado do jogo a ser salvo.
            save_name (str): Nome do salvamento. Se None, usa a data/hora atual.
            
        Returns:
            str: Caminho do arquivo de salvamento ou None se falhar.
        """
        try:
            # Gera um nome de arquivo baseado na data/hora se não for fornecido
            if not save_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = f"save_{timestamp}"
            
            # Garante que o nome do arquivo termina com .save
            if not save_name.endswith('.save'):
                save_name += '.save'
            
            # Caminho completo do arquivo
            save_path = os.path.join(self.save_dir, save_name)
            
            # Adiciona metadados ao salvamento
            save_data = {
                'metadata': {
                    'version': '2.0',
                    'timestamp': datetime.now().isoformat(),
                    'name': save_name
                },
                'game_state': game_state
            }
            # Calcula hash de integridade
            save_data['metadata']['integrity_hash'] = self._compute_hash(save_data['game_state'])
            # Salva como JSON
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Jogo salvo com sucesso em: {save_path}")
            return save_path
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar jogo: {e}", exc_info=True)
            return None

    def load_game(self, save_name: str) -> dict | None:
        """
        Carrega um jogo salvo.
        
        Args:
            save_name (str): Nome do arquivo de salvamento.
            
        Returns:
            dict: Estado do jogo carregado ou None se falhar.
        """
        try:
            # Garante que o nome do arquivo termina com .save
            if not save_name.endswith('.save'):
                save_name += '.save'
            
            # Caminho completo do arquivo
            save_path = os.path.join(self.save_dir, save_name)
            
            # Verifica se o arquivo existe
            if not os.path.exists(save_path):
                self.logger.error(f"Arquivo de salvamento não encontrado: {save_path}")
                return None
            
            # Carrega os dados usando JSON
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Verifica integridade
            expected_hash = save_data['metadata'].get('integrity_hash')
            actual_hash = self._compute_hash(save_data['game_state'])
            if expected_hash != actual_hash:
                self.logger.error(f"Falha na verificação de integridade do save: {save_name}")
                return None
            
            self.logger.info(f"Jogo carregado com sucesso de: {save_path}")
            return save_data['game_state']
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar jogo: {e}", exc_info=True)
            return None
    
    def autosave(self, game_state_getter, interval_sec=120):
        """Inicia um autosave em background a cada interval_sec segundos."""
        def _autosave_loop():
            while True:
                try:
                    state = game_state_getter()
                    self.save_game(state, save_name='autosave')
                except Exception as e:
                    self.logger.error(f"Erro no autosave: {e}")
                time.sleep(interval_sec)
        t = threading.Thread(target=_autosave_loop, daemon=True)
        t.start()
    
    def list_saves(self):
        """
        Lista todos os jogos salvos disponíveis.
        
        Returns:
            list: Lista de dicionários com informações sobre os salvamentos.
        """
        saves = []
        
        try:
            # Lista todos os arquivos .save no diretório
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.save'):
                    save_path = os.path.join(self.save_dir, filename)
                    
                    try:
                        # Tenta carregar os metadados do salvamento
                        with open(save_path, 'r', encoding='utf-8') as f:
                            save_data = json.load(f)
                            metadata = save_data.get('metadata', {})
                            
                            saves.append({
                                'filename': filename,
                                'path': save_path,
                                'name': metadata.get('name', filename),
                                'timestamp': metadata.get('timestamp', ''),
                                'version': metadata.get('version', 'unknown')
                            })
                    except Exception as e:
                        # Se não conseguir carregar os metadados, adiciona informações básicas
                        self.logger.warning(f"Não foi possível ler metadados de {filename}: {e}")
                        saves.append({
                            'filename': filename,
                            'path': save_path,
                            'name': filename,
                            'timestamp': '',
                            'version': 'unknown'
                        })
            
            # Ordena por timestamp (mais recente primeiro)
            saves.sort(key=lambda x: x['timestamp'], reverse=True)
            return saves
            
        except Exception as e:
            self.logger.error(f"Erro ao listar salvamentos: {e}", exc_info=True)
            return []
    
    def delete_save(self, save_name):
        """
        Exclui um jogo salvo.
        
        Args:
            save_name (str): Nome do arquivo de salvamento.
            
        Returns:
            bool: True se bem-sucedido, False caso contrário.
        """
        try:
            # Garante que o nome do arquivo termina com .save
            if not save_name.endswith('.save'):
                save_name += '.save'
            
            # Caminho completo do arquivo
            save_path = os.path.join(self.save_dir, save_name)
            
            # Verifica se o arquivo existe
            if not os.path.exists(save_path):
                self.logger.error(f"Arquivo de salvamento não encontrado: {save_path}")
                return False
            
            # Exclui o arquivo
            os.remove(save_path)
            self.logger.info(f"Salvamento excluído: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao excluir salvamento: {e}", exc_info=True)
            return False
