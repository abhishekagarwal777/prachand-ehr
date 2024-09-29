class ObjectNotFoundException(RuntimeError):
    def __init__(self, obj_type: str, message: str, *args):
        super().__init__(message, *args)
        self._type = obj_type

    @property
    def type(self):
        return self._type

def find_object(obj_id):
    # Simulate an object not found scenario
    raise ObjectNotFoundException("EHR", f"Object with ID {obj_id} not found")

try:
    find_object(123)
except ObjectNotFoundException as e:
    print(f"Exception: {e}, Type: {e.type}")
