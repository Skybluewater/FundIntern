from abc import ABC, abstractmethod


class Serializable(ABC):
    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def from_dict(self, dictionary):
        pass