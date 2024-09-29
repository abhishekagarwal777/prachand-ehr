import json
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union

class RMObject:
    pass

class InternalServerException(Exception):
    pass

class RmDbJson:
    @staticmethod
    def read_tree(db_json_str: str) -> Any:
        try:
            return json.loads(db_json_str)
        except json.JSONDecodeError as e:
            raise InternalServerException(str(e))

    @staticmethod
    def convert_value(decoded: Dict[str, Any], rm_type: type) -> RMObject:
        # Placeholder for conversion logic. Actual implementation would depend on RMObject structure.
        return rm_type()

class RmAttributeAlias:
    @staticmethod
    def get_alias(attribute: str) -> str:
        # Implement alias resolution logic as needed
        return attribute

    @staticmethod
    def get_attribute(alias: str) -> str:
        # Implement reverse alias resolution logic as needed
        return alias

class RmTypeAlias:
    @staticmethod
    def get_rm_type(value: str) -> str:
        # Implement RM type resolution logic as needed
        return value

class DbToRmFormat:
    TYPE_ALIAS = "T"
    TYPE_ATTRIBUTE = "_type"

    @staticmethod
    def reconstruct_from_db_format(rm_type: type, db_json_str: str) -> Optional[RMObject]:
        json_node = DbToRmFormat.parse_json(db_json_str)

        if isinstance(json_node, dict):
            return DbToRmFormat.reconstruct_rm_object(rm_type, json_node)
        elif isinstance(json_node, str):
            return json_node
        elif isinstance(json_node, (int, float)):
            return json_node
        elif isinstance(json_node, bool):
            return json_node
        elif json_node is None:
            return None
        else:
            raise ValueError("Unexpected JSON root array")

    @staticmethod
    def parse_json(db_json_str: str) -> Any:
        return RmDbJson.read_tree(db_json_str)

    @staticmethod
    def reconstruct_rm_object(rm_type: type, db_json_str: str) -> RMObject:
        json_node = DbToRmFormat.parse_json(db_json_str)
        if isinstance(json_node, dict):
            return DbToRmFormat.reconstruct_rm_object(rm_type, json_node)
        else:
            raise ValueError("Unexpected JSON root array")

    @staticmethod
    def reconstruct_rm_object(rm_type: type, json_object: Dict[str, Any]) -> RMObject:
        db_root: Dict[str, Any]

        if DbToRmFormat.TYPE_ALIAS in json_object:
            # plain object
            db_root = json_object
        else:
            by_path = DbToRmFormat.group_by_path(json_object)
            root_path_length = min(len(k) for k in by_path.keys())

            entries = {}
            for key, value in by_path.items():
                remaining = DbToRmFormat.remaining_path(root_path_length, key)
                entries[remaining] = value
            db_root = entries.pop(DbJsonPath.EMPTY_PATH)

            for k, v in entries.items():
                DbToRmFormat.insert_json_entry(db_root, k, v)

        decoded = DbToRmFormat.decode_keys(db_root)
        return RmDbJson.convert_value(decoded, rm_type)

    @staticmethod
    def remaining_path(prefix_len: int, full_path_str: str) -> str:
        if len(full_path_str) > prefix_len and full_path_str[prefix_len] == '.':
            pos = prefix_len + 1
        else:
            pos = prefix_len

        return full_path_str[pos:]

    @staticmethod
    def insert_json_entry(db_root: Dict[str, Any], path: str, value: Dict[str, Any]) -> None:
        parent_object = db_root
        components = path.split('.')
        leaf = components[-1]

        for component in components:
            is_leaf = component == leaf
            child = value
            field_name = component

            if not is_leaf:
                if field_name not in parent_object:
                    raise ValueError(f"missing ancestor {field_name} ({path})")
                parent_object = parent_object[field_name]
            else:
                parent_object[field_name] = child

    @staticmethod
    def decode_keys(db_json: Dict[str, Any]) -> Dict[str, Any]:
        if RmAttributeAlias.get_alias(DbToRmFormat.TYPE_ATTRIBUTE) in db_json:
            DbToRmFormat.revert_node_aliases_in_place(db_json)
        else:
            for value in db_json.values():
                DbToRmFormat.revert_node_aliases_in_place(value)

        return db_json

    @staticmethod
    def revert_node_aliases_in_place(db_json: Any) -> None:
        if isinstance(db_json, dict):
            nodes = list(db_json.items())
            db_json.clear()

            for alias, value in nodes:
                attribute = RmAttributeAlias.get_attribute(alias)
                if DbToRmFormat.TYPE_ATTRIBUTE == attribute:
                    rm_type = RmTypeAlias.get_rm_type(value)
                    db_json[attribute] = rm_type
                else:
                    db_json[attribute] = value
                    DbToRmFormat.revert_node_aliases_in_place(value)
        elif isinstance(db_json, list):
            for item in db_json:
                DbToRmFormat.revert_node_aliases_in_place(item)

    @staticmethod
    def group_by_path(db_json: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        return {key: value for key, value in db_json.items()}

class DbJsonPath:
    EMPTY_PATH = 'EMPTY_PATH'

    def __init__(self, path: str, components: List[Tuple[str, Optional[int]]]):
        self.path = path
        self.components = components

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, DbJsonPath) and self.components == other.components

    def __hash__(self) -> int:
        return hash(tuple(self.components))

    def __str__(self) -> str:
        return f"DbJsonPath{{path={self.path}}}"

    @staticmethod
    def parse(path: str) -> 'DbJsonPath':
        if not path:
            return DbJsonPath.EMPTY_PATH

        components = []
        sb = []
        nr = -1

        for ch in path:
            if ch == '.':
                components.append(( ''.join(sb), nr if nr >= 0 else None))
                nr = -1
                sb.clear()
            elif ch.isdigit():
                if nr < 0:
                    nr = int(ch)
                else:
                    nr = 10 * nr + int(ch)
            else:
                sb.append(ch)

        return DbJsonPath(path, components)

# Note: The actual RMObject class would need to be properly implemented according to your requirements.
