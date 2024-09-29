from typing import Callable, Any

# Define the type for the post-process column function
AqlSqlResultPostprocessor = Callable[[Any], Any]



def process_column(value: Any) -> Any:
    # Implement your processing logic here
    return value

# Assign the function to a variable of type AqlSqlResultPostprocessor
postprocessor: AqlSqlResultPostprocessor = process_column



from typing import Any

class AqlSqlResultPostprocessor:
    def __call__(self, column_value: Any) -> Any:
        """
        Processes a column value.

        Args:
            column_value (Any): The column value to process.

        Returns:
            Any: The processed column value.
        """
        # Implement your processing logic here
        return column_value

# Example usage
postprocessor = AqlSqlResultPostprocessor()
processed_value = postprocessor(column_value)
