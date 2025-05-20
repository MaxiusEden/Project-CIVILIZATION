# game/models/__init__.py
class BaseModel:
    """
    Classe base para todos os modelos do jogo.
    
    Esta classe fornece funcionalidades comuns a todos os modelos,
    como identificação única, serialização e validação.
    """
    
    def __init__(self):
        """Inicializa um novo modelo com um ID único."""
        import uuid
        self.id = str(uuid.uuid4())
        
    def to_dict(self):
        """
        Converte o modelo para um dicionário para serialização.
        
        Returns:
            dict: Representação do modelo como dicionário.
        """
        return {
            'id': self.id
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Cria uma instância do modelo a partir de um dicionário.
        
        Args:
            data (dict): Dicionário contendo os dados do modelo.
            
        Returns:
            BaseModel: Nova instância do modelo.
        """
        instance = cls()
        instance.id = data.get('id', instance.id)
        return instance
    
    def validate(self):
        """
        Valida o estado atual do modelo.
        
        Returns:
            bool: True se o modelo é válido, False caso contrário.
        """
        return True
