from typing import Optional, List, Union, Dict
from abc import ABC, abstractmethod

class AqlFeatureNotImplementedException(Exception):
    pass

class IllegalAqlException(Exception):
    pass

class SystemService:
    def get_system_id(self) -> str:
        pass

class AqlQuery:
    def get_from(self) -> Optional['Containment']:
        pass

class Containment(ABC):
    @abstractmethod
    def accept(self, visitor: 'ContainmentVisitor'):
        pass

class ContainmentClassExpression(Containment):
    def __init__(self, type: str, contains: Optional[Containment]):
        self.type = type
        self.contains = contains

    def accept(self, visitor: 'ContainmentVisitor'):
        visitor.visit_class_expression(self)

class ContainmentVersionExpression(Containment):
    def __init__(self, contains: Optional[Containment]):
        self.contains = contains

    def accept(self, visitor: 'ContainmentVisitor'):
        visitor.visit_version_expression(self)

class ContainmentSetOperator(Containment):
    def __init__(self, values: List[Containment]):
        self.values = values

    def accept(self, visitor: 'ContainmentVisitor'):
        visitor.visit_set_operator(self)

class ContainmentNotOperator(Containment):
    def accept(self, visitor: 'ContainmentVisitor'):
        visitor.visit_not_operator(self)

class ContainmentVisitor(ABC):
    @abstractmethod
    def visit_class_expression(self, expr: ContainmentClassExpression):
        pass
    
    @abstractmethod
    def visit_version_expression(self, expr: ContainmentVersionExpression):
        pass
    
    @abstractmethod
    def visit_set_operator(self, expr: ContainmentSetOperator):
        pass
    
    @abstractmethod
    def visit_not_operator(self, expr: ContainmentNotOperator):
        pass

class FromCheck:
    def __init__(self, system_service: SystemService):
        self.system_service = system_service

    def ensure_supported(self, aql_query: AqlQuery):
        current_containment = aql_query.get_from()
        if current_containment is None:
            raise AqlFeatureNotImplementedException("FROM must be specified")
        
        if isinstance(current_containment, ContainmentClassExpression) and current_containment.type == "EHR":
            current_containment = current_containment.contains
        elif not isinstance(current_containment, AbstractContainmentExpression):
            raise AqlFeatureNotImplementedException("AND/OR/NOT only allowed after CONTAINS")
        
        self.ensure_containment_supported(current_containment, None)
        self.ensure_containment_predicate_supported(current_containment)

    def ensure_containment_supported(self, containment: Optional[Containment], parent_structure: Optional[str]):
        if containment is None:
            return
        
        if isinstance(containment, ContainmentClassExpression):
            next_containment, structure_root = self.ensure_structure_contains_supported(containment, parent_structure)
            self.ensure_containment_supported(next_containment, structure_root)
            self.ensure_containment_structure_supported(parent_structure, containment, structure_root)
        elif isinstance(containment, ContainmentVersionExpression):
            self.ensure_version_containment_supported(containment)
        elif isinstance(containment, ContainmentSetOperator):
            for nc in containment.values:
                self.ensure_containment_supported(nc, parent_structure)
        elif isinstance(containment, ContainmentNotOperator):
            raise AqlFeatureNotImplementedException("NOT CONTAINS")
        else:
            raise IllegalAqlException(f"Unknown containment type: {type(containment).__name__}")

    def ensure_version_containment_supported(self, cve: ContainmentVersionExpression):
        next_containment = cve.contains
        if next_containment is None:
            raise IllegalAqlException("VERSION containment must be followed by another CONTAINS expression")
        if isinstance(next_containment, ContainmentVersionExpression):
            raise IllegalAqlException("VERSION cannot contain another VERSION")
        if isinstance(next_containment, (ContainmentSetOperator, ContainmentNotOperator)):
            raise AqlFeatureNotImplementedException("AND/OR/NOT operator as next containment after VERSION")
        self.ensure_containment_supported(next_containment, None)

    def ensure_structure_contains_supported(self, containment: ContainmentClassExpression, structure: Optional[str]):
        # Add logic here based on your specific application
        # This is just a placeholder for the actual implementation
        structure_rm_types = self.get_structure_rm_types(containment.type)
        if "FOLDER" in structure_rm_types:
            raise AqlFeatureNotImplementedException(f"CONTAINS {containment.type} is not supported")
        if not all(self.is_structure_entry(rm_type) for rm_type in structure_rm_types):
            raise AqlFeatureNotImplementedException(f"CONTAINS {containment.type} is currently not supported")
        if structure is None and any(self.get_structure_root(rm_type) is None for rm_type in structure_rm_types):
            raise IllegalAqlException(f"It is unclear if {containment.type} targets a COMPOSITION or EHR_STATUS")
        structure_root = self.get_common_structure_root(structure_rm_types)
        return containment.contains, structure_root

    def ensure_containment_structure_supported(self, parent_structure: Optional[str], cce: ContainmentClassExpression, structure: Optional[str]):
        if parent_structure is None:
            if structure is None:
                raise IllegalAqlException(f"Structure {parent_structure} cannot CONTAIN {cce.type} (of structure {structure})")
        elif parent_structure == "FOLDER":
            if structure not in ["FOLDER", "COMPOSITION"]:
                raise IllegalAqlException(f"Structure {parent_structure} cannot CONTAIN {cce.type} (of structure {structure})")
        elif parent_structure in ["COMPOSITION", "EHR_STATUS"]:
            if parent_structure != structure:
                raise IllegalAqlException(f"Structure {parent_structure} cannot CONTAIN {cce.type} (of structure {structure})")
        else:
            raise RuntimeError(f"{parent_structure} is not root structure")

    def ensure_containment_predicate_supported(self, containment: Containment):
        if isinstance(containment, ContainmentVersionExpression):
            p_type = containment.get_version_predicate_type()
            if p_type not in ["LATEST_VERSION", "NONE"]:
                raise AqlFeatureNotImplementedException("Only VERSION queries without predicate or on LATEST_VERSION supported")
        # Add additional predicate checks here

    def get_structure_rm_types(self, type_name: str):
        # Replace with actual implementation
        pass

    def is_structure_entry(self, rm_type: str) -> bool:
        # Replace with actual implementation
        pass

    def get_structure_root(self, rm_type: str) -> Optional[str]:
        # Replace with actual implementation
        pass

    def get_common_structure_root(self, rm_types: List[str]) -> Optional[str]:
        # Replace with actual implementation
        pass
