from abc import ABC, abstractmethod

class IExtractor(ABC):
    @abstractmethod
    def extract_data(self):
        pass

class IAnnouncement(ABC):
    @abstractmethod
    def announce(self):
        pass
