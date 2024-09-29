from typing import Any, Dict, Callable
from aspectlib import Aspect, ProceedingJoinPoint
from EHR.dto import QueryWithParameters
from EHR.extensionpoints import QueryExtensionPoint
from EHR.plugin import AbstractPluginAspect

class QueryPluginAspect(AbstractPluginAspect):
    """Aspect for handling plugin extension points for queries."""

    def __init__(self, bean_factory: Any):
        super().__init__(bean_factory, QueryExtensionPoint)

    @Aspect
    def around_query_execute(self, pjp: ProceedingJoinPoint) -> Any:
        """Handle extension points for executing queries.

        Args:
            pjp: The proceeding join point.

        Returns:
            The result of the query execution after applying plugin extensions.
        """
        return self.proceed_with_plugin_extension_points(
            pjp,
            QueryExtensionPoint.around_query_execution,
            lambda args: QueryWithParameters(str(args[0]), dict(args[1])),
            lambda i, args: (i.query, i.parameters)
        )

# Example usage (if needed)
if __name__ == "__main__":
    # This is where you'd initialize your Spring-like context and run the application
    pass
