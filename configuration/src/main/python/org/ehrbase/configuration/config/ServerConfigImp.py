from pydantic import BaseModel, Field, conint

class ServerConfigImp(BaseModel):
    port: conint(ge=1025, le=65536)  # Constrained integer for port range
    disable_strict_validation: bool = False

    class Config:
        fields = {
            'disable_strict_validation': 'disableStrictValidation'
        }

# Example usage
config = ServerConfigImp(port=8080)
print(config.port)
print(config.disable_strict_validation)
