# Import required modules and classes
from sqlalchemy import (
    Table, Column, Integer, String, ForeignKey, func, case, literal, select, text, null
)
from sqlalchemy.sql import and_, or_, literal_column
from sqlalchemy.sql.expression import alias, distinct
from collections import OrderedDict
from functools import wraps

import logging
from typing import Optional, List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

# Define utility functions
def sql_aggregating_field(af, src, asl_query_to_table):
    if (src is None or af.get("base_field") is None) and af.get("function") != "COUNT":
        raise ValueError("only count does not require a source table")
    
    is_extracted_column = (
        af.get("base_field", {}).get("extracted_column") not in {
            "OV_TIME_COMMITTED", "OV_TIME_COMMITTED_DV", "EHR_TIME_CREATED_DV", "EHR_TIME_CREATED"
        }
    )
    
    if is_extracted_column and af.get("function") != "COUNT":
        raise ValueError(f"Aggregate function {af.get('function')} is not allowed for extracted columns")
    
    aggregate_function = to_aggregated_field_function(af)
    field = field_to_aggregate(src, af, asl_query_to_table)
    
    return aggregate_function(field)

def field_to_aggregate(src, af, asl_query_to_table):
    base_field = af.get("base_field")
    
    if base_field is None:
        return None
    elif isinstance(base_field, dict) and base_field.get("type") == "AslColumnField":
        return field(src, base_field, True)
    elif isinstance(base_field, dict) and base_field.get("type") == "AslComplexExtractedColumnField":
        extracted_column = base_field.get("extracted_column")
        if extracted_column == "VO_ID":
            return field(src, base_field, "COMP_DATA.VO_ID", True)
        elif extracted_column == "ARCHETYPE_NODE_ID":
            return func.row(field(src, base_field, "COMP_DATA.RM_ENTITY", True),
                            field(src, base_field, "COMP_DATA.ENTITY_CONCEPT", True))
        else:
            raise ValueError(f"{extracted_column} is not a complex extracted column")
    elif isinstance(base_field, dict) and base_field.get("type") == "AslConstantField":
        return literal(base_field.get("value"))
    elif isinstance(base_field, dict) and base_field.get("type") == "AslSubqueryField":
        return subquery_field(base_field, asl_query_to_table)
    else:
        raise ValueError(f"Unknown field type: {base_field}")

def to_aggregated_field_function(af):
    func_name = af.get("function")
    
    if func_name == "COUNT":
        return lambda f: func.count(distinct(f)) if af.get("is_distinct") else func.count(f)
    elif func_name == "MIN":
        return lambda f: func.min(f)
    elif func_name == "MAX":
        return lambda f: func.max(f)
    elif func_name == "SUM":
        return lambda f: func.sum(f)
    elif func_name == "AVG":
        return lambda f: func.avg(f)
    else:
        raise ValueError(f"Unknown aggregate function: {func_name}")

def subquery_field(sqf, asl_query_to_table):
    base_query = sqf.get("base_query")
    
    if not isinstance(base_query, dict) or base_query.get("type") != "AslRmObjectDataQuery":
        raise ValueError(f"Subquery field not supported for type: {type(base_query)}")
    
    # Build subquery based on the query data (you will need to implement this function)
    subquery = build_data_subquery(base_query, asl_query_to_table, sqf.get("filter_conditions"))
    
    return subquery.label(sqf.get("name"))

def apply_pg_llj_workaround(child_query, join, relation):
    workaround_needed = (
        join.get("join_type") not in {None, "JOIN"} and not isinstance(child_query, dict)
    )
    
    if workaround_needed:
        fields = [func.coalesce(f).label(f.key) for f in relation.columns]
        return fields
    return relation.columns

# Utility for building data subqueries (implementation can vary)
def build_data_subquery(aq, asl_query_to_table, conditions):
    # Implement the logic to build subquery based on conditions
    pass
