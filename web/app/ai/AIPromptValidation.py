from abc import abstractmethod, ABC


class AIPromptValidation(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def sanitize_values(**kwargs):
        for key, value in kwargs.items():
            pass

    @classmethod
    @abstractmethod
    def validate_values(cls, **kwargs):
        for key, value in kwargs.items():
            pass
