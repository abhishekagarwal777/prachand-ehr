from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import JSONB, BIGINT

class AdditionalSQLFunctions:
    
    @staticmethod
    def jsonb_array_elements(jsonb_array):
        return func.jsonb_array_elements(jsonb_array)
    
    @staticmethod
    def jsonb_extract_path_text(jsonb, *path):
        return func.jsonb_extract_path_text(jsonb, *path)
    
    @staticmethod
    def jsonb_dv_ordered_magnitude(dv_ordered_field):
        return func.jsonb_dv_ordered_magnitude(dv_ordered_field)
    
    @staticmethod
    def jsonb_attribute_path_text(jsonb, *path):
        # SQLAlchemy does not have built-in support for chaining JSONB operations, so we need to build it manually
        jsonb_field = jsonb
        for att in path:
            jsonb_field = func.jsonb_get_attribute(jsonb_field, text(att))
        return func.jsonb_get_element_as_text(jsonb_field, text("0"))
    
    @staticmethod
    def to_jsonb(value):
        if isinstance(value, str):
            return func.to_jsonb(text(value))
        return func.to_jsonb(value)
    
    @staticmethod
    def max_dv_ordered(field):
        return func.max_dv_ordered(field).label('max_dv_ordered')
    
    @staticmethod
    def min_dv_ordered(field):
        return func.min_dv_ordered(field).label('min_dv_ordered')
    
    @staticmethod
    def count(distinct, field):
        if distinct:
            return func.count_distinct(field).cast(BIGINT)
        return func.count(field).cast(BIGINT) if field is not None else func.count('*').cast(BIGINT)
