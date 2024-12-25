from abc import ABC, abstractmethod
from data.serializable import Serializable

class BaseExtractor(Serializable, ABC):
    def __init__(self, announcement):
        self.announcement = announcement
        self.stock_in = None
        self.stock_out = None

    @abstractmethod
    def extract_stock_info(file_handler):
        pass

    def to_dict(self):
        return {
            "stock_in": self.stock_in,
            "stock_out": self.stock_out
        }
    
    def from_dict(self, dictionary):
        pass