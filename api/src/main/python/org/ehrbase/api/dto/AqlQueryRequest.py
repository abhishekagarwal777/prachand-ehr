from dataclasses import dataclass, field
from typing import Dict, Optional, Any
import json

@dataclass
class AqlQueryRequest:
    query_string: str
    parameters: Optional[Dict[str, Any]] = field(default_factory=dict)
    fetch: Optional[int] = None
    offset: Optional[int] = None

    def __post_init__(self):
        if self.parameters is not None:
            self.parameters = {
                k: self.handle_explicit_parameter_types(v)
                for k, v in self.parameters.items()
            }

    @staticmethod
    def handle_explicit_parameter_types(param_value: Any) -> Any:
        if isinstance(param_value, dict):
            param_type = param_value.get("type")
            if isinstance(param_type, str):
                if param_type == "int":
                    try:
                        return int(param_value.get("value", 0))
                    except ValueError:
                        return param_value
                elif param_type == "num":
                    try:
                        return float(param_value.get("value", 0.0))
                    except ValueError:
                        return param_value
        return param_value


# Example instantiation
request = AqlQueryRequest(
    query_string="SELECT * FROM EHR WHERE status = :status",
    parameters={"status": {"type": "string", "value": "active"}},
    fetch=10,
    offset=0
)

print(request)
