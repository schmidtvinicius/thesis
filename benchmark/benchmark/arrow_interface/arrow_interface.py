from abc import ABC, abstractmethod

class ArrowInterface(ABC):

    def __init__(self, **kwargs):
        super().__init__()

    
    @abstractmethod
    def write_to_table(self, data) -> None: ...


    @abstractmethod
    def read_table(self): ...
    