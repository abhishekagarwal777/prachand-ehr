from abc import ABC, abstractmethod

class HttpCtxMap(dict):
    """Custom dictionary to represent HTTP context map."""
    pass

class HttpRestContextHandler(ABC):
    @abstractmethod
    def handle(self, context: HttpCtxMap):
        """Handle the HTTP context map."""
        pass
