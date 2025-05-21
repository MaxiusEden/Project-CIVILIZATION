class BaseModel:
    """
    Classe base para todos os modelos do jogo.
    """
    def __init__(self):
        import uuid
        self.id = str(uuid.uuid4())

    def to_dict(self):
        return {'id': self.id}

    @classmethod
    def from_dict(cls, data):
        instance = cls()
        instance.id = data.get('id', instance.id)
        return instance

    def validate(self):
        return True