from typing import Callable
from ehrscape import QueryResultDto  # Adjust import based on your project structure
from dto import QueryWithParameters    # Adjust import based on your project structure

class QueryExtensionPoint:
    """
    Extension Point for Query handling.
    """

    def around_query_execution(self, input: QueryWithParameters, 
                                chain: Callable[[QueryWithParameters], QueryResultDto]) -> QueryResultDto:
        """
        Intercept Query execution.

        Args:
            input: Aql String to be executed encapsulated in QueryWithParameters.
            chain: Next Extension Point function.

        Returns:
            QueryResultDto: Result of the query.
        """
        return chain(input)
