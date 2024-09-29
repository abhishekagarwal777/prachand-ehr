import re
import uuid
from typing import List, Set, Optional
from collections import namedtuple

from aql_sdk import AqlObjectPath, IdentifiedPath, AbstractContainmentExpression, ContainmentClassExpression, ContainmentVersionExpression
from aql_sdk.exceptions import AqlFeatureNotImplementedException, IllegalAqlException
from aql_sdk.util import AqlUtil
from aql_sdk.rmconstants import RmConstants
from aql_sdk.pathanalysis import ANode, PathAnalysis
from aql_sdk.asl.model import AslExtractedColumn, AslRmTypeAndConcept

FeatureCheckUtils = namedtuple('FeatureCheckUtils', ['RM_INFO_LOOKUP', 'DV_ORDERED_TYPES', 'OBJECT_VERSION_ID_REGEX', 'SUPPORTED_VERSION_PATHS'])

def create_feature_check_utils():
    RM_INFO_LOOKUP = ArchieRMInfoLookup.getInstance()
    DV_ORDERED_TYPES = set(
        RM_INFO_LOOKUP.getTypeInfo(DvOrdered).getAllDescendantClasses()
        .filter(lambda t: not Modifier.isAbstract(t.getJavaClass().getModifiers()))
        .map(RMTypeInfo::getRmName)
    )
    OBJECT_VERSION_ID_REGEX = re.compile(r"([a-fA-F0-9-]{36})(::([^:]*)::([1-9]\d*))?")

    SUPPORTED_VERSION_PATHS = [
        (["uid", "value"], {ClauseType.SELECT, ClauseType.WHERE, ClauseType.ORDER_BY}),
        (["commit_audit", "time_committed"], {ClauseType.SELECT, ClauseType.WHERE, ClauseType.ORDER_BY}),
        (["commit_audit", "time_committed", "value"], {ClauseType.SELECT}),
        (["commit_audit", "system_id"], {ClauseType.SELECT, ClauseType.WHERE}),
        (["commit_audit", "description"], {ClauseType.SELECT}),
        (["commit_audit", "description", "value"], {ClauseType.SELECT, ClauseType.WHERE, ClauseType.ORDER_BY}),
        (["commit_audit", "change_type"], {ClauseType.SELECT}),
        (["commit_audit", "change_type", "value"], {ClauseType.SELECT, ClauseType.WHERE, ClauseType.ORDER_BY}),
        (["commit_audit", "change_type", "defining_code", "code_string"], {ClauseType.SELECT, ClauseType.WHERE, ClauseType.ORDER_BY}),
        (["commit_audit", "change_type", "defining_code", "preferred_term"], {ClauseType.SELECT, ClauseType.WHERE, ClauseType.ORDER_BY}),
        (["commit_audit", "change_type", "defining_code", "terminology_id", "value"], {ClauseType.SELECT, ClauseType.WHERE}),
        (["contribution", "id", "value"], {ClauseType.SELECT, ClauseType.WHERE, ClauseType.ORDER_BY}),
    ]
    return FeatureCheckUtils(RM_INFO_LOOKUP, DV_ORDERED_TYPES, OBJECT_VERSION_ID_REGEX, SUPPORTED_VERSION_PATHS)


def starts_with(successor: IdentifiedPath, predecessor: IdentifiedPath) -> bool:
    if successor == predecessor:
        return True
    if successor is None or predecessor is None:
        return False
    if successor.getRoot() != predecessor.getRoot():
        return False
    if successor.getRootPredicate() != predecessor.getRootPredicate():
        return False

    successor_path_nodes = successor.getPath().getPathNodes() if successor else []
    predecessor_path_nodes = predecessor.getPath().getPathNodes() if predecessor else []
    predecessor_size = len(predecessor_path_nodes)
    if len(successor_path_nodes) < predecessor_size:
        return False
    return predecessor_path_nodes == successor_path_nodes[:predecessor_size]


def ensure_path_predicate_supported(path: AqlObjectPath, node_type: str, predicate: List[AndOperatorPredicate], system_id: str):
    for p in AqlUtil.streamPredicates(predicate):
        extracted_column = AslExtractedColumn.find(node_type, p.getPath())
        if extracted_column is None:
            raise AqlFeatureNotImplementedException(f"Path predicate {AqlRenderer.renderPredicate(predicate)} in path {path} contains unsupported path {p.getPath()}")
        if extracted_column == AslExtractedColumn.ARCHETYPE_NODE_ID and p.getOperator() not in {ComparisonOperatorPredicate.PredicateComparisonOperator.EQ, ComparisonOperatorPredicate.PredicateComparisonOperator.NEQ}:
            raise AqlFeatureNotImplementedException("Predicates on 'archetype_node_id' only support = and !=")
        ensure_operand_supported(PathDetails(extracted_column, {node_type}), p.getValue(), system_id)


def find_supported_identified_path(ip: IdentifiedPath, allow_empty: bool, clause_type: ClauseType, system_id: str) -> PathDetails:
    path = ip.getPath()
    root = ip.getRoot()
    containment_type = root.getType() if isinstance(root, ContainmentClassExpression) else RmConstants.ORIGINAL_VERSION
    is_version_path = containment_type == RmConstants.ORIGINAL_VERSION
    if path is None:
        if allow_empty:
            if is_version_path:
                raise AqlFeatureNotImplementedException(f"selecting the full VERSION object ({root.getIdentifier()})")
            if containment_type == RmConstants.EHR:
                raise AqlFeatureNotImplementedException(f"selecting the full EHR object ({root.getIdentifier()})")
            return PathDetails(
                None,
                set(
                    AncestorStructureRmType.byTypeName(containment_type)
                    .map(lambda x: x.getDescendants())
                    .map(lambda s: {StructureRmType.name for s in s})
                    .orElse({containment_type})
                )
            )
        else:
            raise AqlFeatureNotImplementedException(f"{clause_type}: identified path for type {containment_type} is missing")

    if containment_type == RmConstants.EHR:
        return AslExtractedColumn.find(containment_type, path).filter(lambda ec: ec not in {AslExtractedColumn.EHR_TIME_CREATED, AslExtractedColumn.EHR_SYSTEM_ID_DV} or clause_type == ClauseType.SELECT).map(lambda ec: PathDetails(ec, {"String"})).orElseThrow(
            lambda: AqlFeatureNotImplementedException(f"{clause_type}: identified path '{path.render()}' for type {containment_type} not supported")
        )

    path_attributes = [node.getAttribute() for node in path.getPathNodes()]
    if is_version_path and all(p != path_attributes for p, _ in SUPPORTED_VERSION_PATHS if clause_type in _):
        raise AqlFeatureNotImplementedException(f"{clause_type}: VERSION path {root.getIdentifier()}/{path.render()} is not supported")

    level = -1
    analyzed = PathAnalysis.analyzeAqlPathTypes(containment_type, ip.getRootPredicate(), root.getPredicates(), path, None)
    if not analyzed.getCandidateTypes():
        raise IllegalAqlException(f"{ip.render()} is not a valid RM path")

    attribute_infos = PathAnalysis.createAttributeInfos(analyzed)
    target_types = set()
    parent_target_types = set(
        AncestorStructureRmType.byTypeName(containment_type)
        .map(lambda x: x.getDescendants())
        .map(lambda s: {StructureRmType.name for s in s})
        .orElse({containment_type})
    )
    for i, path_node in enumerate(path.getPathNodes()):
        attribute = path_attributes[i]
        analyzed_parent = analyzed
        analyzed = analyzed.getAttribute(attribute)
        level += 1
        target_types = {
            t for t in attribute_infos.get(analyzed_parent).get(attribute).targetTypes()
            if not is_version_path or not attribute == "commit_audit" or RmConstants.AUDIT_DETAILS == t
        }
        categories = analyzed.getCategories()
        if ANode.NodeCategory.STRUCTURE_INTERMEDIATE in categories:
            raise AqlFeatureNotImplementedException(f"{clause_type}: path {path.render()} contains STRUCTURE_INTERMEDIATE attribute {attribute}")
        if clause_type == ClauseType.WHERE and i == len(path.getPathNodes()) - 1 and not any(
            t for t in target_types
            if RM_INFO_LOOKUP.getTypeInfo(t) is None or t in DV_ORDERED_TYPES
        ):
            raise AqlFeatureNotImplementedException(f"{clause_type}: path {path.render()} only targets types that are not derived from DV_ORDERED and not primitive")
        if len(categories) != 1 or categories.isdisjoint({ANode.NodeCategory.STRUCTURE}):
            sub_path = AqlObjectPath(path.getPathNodes()[level:])
            current_parent_target_types = parent_target_types
            extracted_column = AslExtractedColumn.find(
                current_parent_target_types.pop(), sub_path
            ).filter(lambda ec: ec.getAllowedRmTypes().issubset(current_parent_target_types))

            if extracted_column is None:
                if AqlUtil.streamPredicates(path_node.getPredicateOrOperands()).find_any():
                    raise AqlFeatureNotImplementedException(f"{clause_type}: path {path.render()} contains a non-structure attribute ({attribute}) with at least one predicate")
            else:
                for j in range(1, len(sub_path.getPathNodes())):
                    node = sub_path.getPathNodes()[j]
                    analyzed_parent = analyzed
                    analyzed = analyzed.getAttribute(node.getAttribute())
                    target_types = attribute_infos.get(analyzed_parent).get(node.getAttribute()).targetTypes()
                return PathDetails(extracted_column, target_types)
        target_types.update(t for t in target_types if ensure_path_predicate_supported(path, t, path_node.getPredicateOrOperands(), system_id))
        parent
