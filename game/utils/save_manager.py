# game/utils/save_manager.py
import json
import os
import logging
from datetime import datetime
import pickle

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
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Cria o diretório de salvamentos se não existir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def save_game(self, game_state, save_name=None):
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
                    'version': '1.0',
                    'timestamp': datetime.now().isoformat(),
                    'name': save_name
                },
                'game_state': game_state
            }
            
            # Salva os dados usando pickle para preservar objetos Python
            with open(save_path, 'wb') as f:
                pickle.dump(save_data, f)
            
            self.logger.info(f"Jogo salvo com sucesso em: {save_path}")
            return save_path
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar jogo: {e}", exc_info=True)
            return None
    
    def load_game(self, save_name):
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
            
            # Carrega os dados usando pickle
            with open(save_path, 'rb') as f:
                save_data = pickle.load(f)
            
            self.logger.info(f"Jogo carregado com sucesso de: {save_path}")
            return save_data['game_state']
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar jogo: {e}", exc_info=True)
            return None
    
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
                        with open(save_path, 'rb') as f:
                            save_data = pickle.load(f)
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
