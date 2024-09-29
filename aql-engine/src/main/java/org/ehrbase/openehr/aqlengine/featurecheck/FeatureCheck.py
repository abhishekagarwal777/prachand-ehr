from abc import ABC, abstractmethod

class FeatureCheck(ABC):
    
    @abstractmethod
    def ensure_supported(self, aql_query):
        pass
