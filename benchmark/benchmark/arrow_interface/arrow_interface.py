from abc import ABC, abstractmethod

class ArrowInterface(ABC):

    
    @abstractmethod
    def write_to_table(self, data) -> tuple[float,float]: ...


    @abstractmethod
    def read_table(self): ...


    @abstractmethod
    def create_table(self): ...


    @abstractmethod
    def delete_table(self): ...

    