import threading

class CtxAttr:
    """Base class for context attributes."""
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, CtxAttr):
            return self.name == other.name
        return False

# Concrete Context Attributes
class Query(CtxAttr):
    def __init__(self):
        super().__init__('Query')

class EhrId(CtxAttr):
    def __init__(self):
        super().__init__('EhrId')

class Version(CtxAttr):
    def __init__(self):
        super().__init__('Version')

# Define more attributes as needed...

# Context storage
class HttpRestContext:
    _thread_local = threading.local()
    
    @classmethod
    def _get_context(cls):
        if not hasattr(cls._thread_local, 'context'):
            cls._thread_local.context = {}
        return cls._thread_local.context
    
    @classmethod
    def clear(cls):
        cls._thread_local.context = {}

    @classmethod
    def get_value_by(cls, key):
        return cls._get_context().get(key)
    
    @classmethod
    def register(cls, *args):
        ctx = cls._get_context()
        for key, value in args:
            ctx[key] = value
    
    @classmethod
    def handle(cls, handler):
        handler(cls._get_context())
