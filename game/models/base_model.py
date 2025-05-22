import uuid
from typing import Any, Dict, Type, TypeVar
from game.utils.logger import get_game_logger

T = TypeVar('T', bound='BaseModel')

class BaseModel:
    """
    Classe base para todos os modelos do jogo, com serialização/deserialização recursiva e validação básica.
    """
    required_fields: list[str] = []  # Pode ser sobrescrito nas subclasses

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.logger = get_game_logger(self.__class__.__name__)

    def to_dict(self) -> Dict[str, Any]:
        result = {'id': self.id}
        for attr, value in self.__dict__.items():
            if attr == 'id':
                continue
            if isinstance(value, BaseModel):
                result[attr] = value.to_dict()
            elif isinstance(value, list):
                result[attr] = [v.to_dict() if isinstance(v, BaseModel) else v for v in value]
            else:
                result[attr] = value
        return result

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        instance = cls(id=data.get('id'))
        for attr, value in data.items():
            if attr == 'id':
                continue
            if hasattr(cls, attr):
                attr_type = getattr(cls, attr)
                if isinstance(attr_type, type) and issubclass(attr_type, BaseModel) and isinstance(value, dict):
                    setattr(instance, attr, attr_type.from_dict(value))
                elif isinstance(value, list):
                    # Tenta desserializar listas de modelos
                    if hasattr(attr_type, '__origin__') and attr_type.__origin__ == list:
                        item_type = attr_type.__args__[0]
                        if isinstance(item_type, type) and issubclass(item_type, BaseModel):
                            setattr(instance, attr, [item_type.from_dict(v) if isinstance(v, dict) else v for v in value])
                        else:
                            setattr(instance, attr, value)
                    else:
                        setattr(instance, attr, value)
                else:
                    setattr(instance, attr, value)
            else:
                setattr(instance, attr, value)
        return instance

    def validate(self) -> bool:
        """Valida se os campos obrigatórios estão presentes e não nulos."""
        for field in self.required_fields:
            if not hasattr(self, field) or getattr(self, field) is None:
                return False
        return True