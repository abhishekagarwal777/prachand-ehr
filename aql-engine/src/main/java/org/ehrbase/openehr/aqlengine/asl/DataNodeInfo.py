from typing import List, Optional, Set, Stream, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Placeholder imports for Asl classes
from some_module import (
    AslExtractedColumn, AslEncapsulatingQuery, AslQuery, PathCohesionTreeNode, PathNode
)

class DataNodeInfo(ABC):
    @abstractmethod
    def node(self) -> PathCohesionTreeNode:
        pass

    @abstractmethod
    def parent(self) -> 'OwnerProviderTuple':
        pass

    @abstractmethod
    def provider_sub_query(self) -> AslQuery:
        pass

@dataclass
class JsonRmDataNodeInfo(DataNodeInfo):
    node: PathCohesionTreeNode
    parent: 'OwnerProviderTuple'
    parent_join: AslEncapsulatingQuery
    provider_sub_query: AslQuery
    path_in_json: List[PathNode]
    multiple_valued: bool
    dependent_path_data_nodes: Stream['DataNodeInfo']
    dv_ordered_types: Set[str]
    type: Type

@dataclass
class ExtractedColumnDataNodeInfo(DataNodeInfo):
    node: PathCohesionTreeNode
    parent: 'OwnerProviderTuple'
    provider_sub_query: AslQuery
    extracted_column: AslExtractedColumn

@dataclass
class StructureRmDataNodeInfo(DataNodeInfo):
    node: PathCohesionTreeNode
    parent: 'OwnerProviderTuple'
    parent_join: AslEncapsulatingQuery
    provider_sub_query: AslQuery
