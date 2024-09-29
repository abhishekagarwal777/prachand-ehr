from typing import Optional, Union

class SelectType:
    PATH = 'path'
    PRIMITIVE = 'primitive'
    AGGREGATE_FUNCTION = 'aggregate_function'
    FUNCTION = 'function'

class SelectExpression:
    # Placeholder for the SelectExpression class
    def __init__(self, alias: str, column_expression: Optional[Union['IdentifiedPath', 'AggregateFunction']] = None):
        self._alias = alias
        self._column_expression = column_expression

    def get_alias(self) -> str:
        return self._alias

    def get_column_expression(self) -> Optional[Union['IdentifiedPath', 'AggregateFunction']]:
        return self._column_expression

class IdentifiedPath:
    def __init__(self, path: str):
        self._path = path

    def get_path(self) -> str:
        return self._path

class AggregateFunction:
    def __init__(self, identified_path: IdentifiedPath, function_name: str):
        self._identified_path = identified_path
        self._function_name = function_name

    def get_identified_path(self) -> IdentifiedPath:
        return self._identified_path

    def get_function_name(self) -> str:
        return self._function_name

class CountDistinctAggregateFunction(AggregateFunction):
    pass

class Primitive:
    # Placeholder for the Primitive class
    pass

class ContainsWrapper:
    # Placeholder for the ContainsWrapper class
    def alias(self) -> str:
        return "alias"

class AqlObjectPath:
    @staticmethod
    def render(path: str) -> str:
        return path

class SelectWrapper:
    def __init__(self, select_expression: SelectExpression, select_type: str, root: ContainsWrapper):
        self._select_expression = select_expression
        self._type = select_type
        self._root = root

    def get_select_alias(self) -> str:
        return self._select_expression.get_alias()

    def get_identified_path(self) -> Optional[IdentifiedPath]:
        if self._type == SelectType.PATH:
            return self._select_expression.get_column_expression()
        elif self._type == SelectType.AGGREGATE_FUNCTION:
            expr = self._select_expression.get_column_expression()
            if isinstance(expr, AggregateFunction):
                return expr.get_identified_path()
        return None

    def get_aggregate_function_name(self) -> str:
        if self._type == SelectType.AGGREGATE_FUNCTION:
            expr = self._select_expression.get_column_expression()
            if isinstance(expr, AggregateFunction):
                return expr.get_function_name()
        raise NotImplementedError("Not an aggregate function")

    def is_count_distinct(self) -> bool:
        if self._type == SelectType.AGGREGATE_FUNCTION:
            expr = self._select_expression.get_column_expression()
            return isinstance(expr, CountDistinctAggregateFunction)
        raise NotImplementedError("Not an aggregate function")

    def get_primitive(self) -> Primitive:
        if self._type == SelectType.PRIMITIVE:
            expr = self._select_expression.get_column_expression()
            if isinstance(expr, Primitive):
                return expr
        raise NotImplementedError("Not a primitive")

    def get_select_path(self) -> Optional[str]:
        if self._type == SelectType.PATH:
            path = self.get_identified_path()
            if path:
                return f"{self._root.alias()}/{AqlObjectPath.render(path.get_path())}"
        return None

    def select_expression(self) -> SelectExpression:
        return self._select_expression

    def type(self) -> str:
        return self._type

    def root(self) -> ContainsWrapper:
        return self._root

    def __str__(self) -> str:
        return f"SelectWrapper[selectExpression={self._select_expression}, type={self._type}, root={self._root}]"

# Example of usage
select_expression = SelectExpression(alias="alias", column_expression=IdentifiedPath("path/to/element"))
root = ContainsWrapper()
select_wrapper = SelectWrapper(
    select_expression=select_expression,
    select_type=SelectType.PATH,
    root=root
)
print(select_wrapper)
