from abc import ABC, abstractmethod
from data.data import Announcement

class BaseExtractor(ABC):
    def __init__(self, announcement: Announcement):
        self.announcement = announcement

    @abstractmethod
    def extract_stock_info(file_handler):
        pass