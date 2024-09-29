from typing import Any
from aspectlib import Aspect, ProceedingJoinPoint
from EHR.extensionpoints import TemplateExtensionPoint
from EHR.plugin import AbstractPluginAspect
from openehr.schemas.v1 import OPERATIONALTEMPLATE

class TemplatePluginAspect(AbstractPluginAspect):
    """Aspect for handling plugin extension points for templates."""

    def __init__(self, bean_factory: Any):
        super().__init__(bean_factory, TemplateExtensionPoint)

    @Aspect
    def around_create_template(self, pjp: ProceedingJoinPoint) -> Any:
        """Handle extension points for creating templates.

        Args:
            pjp: The proceeding join point.

        Returns:
            The result of the template creation after applying plugin extensions.
        """
        return self.proceed_with_plugin_extension_points(
            pjp,
            TemplateExtensionPoint.around_creation,
            lambda args: OPERATIONALTEMPLATE(args[0]),  # Assuming args[0] is of type OPERATIONALTEMPLATE
            lambda i, args: (i,)  # Set args[0] to i (the OperationalTemplate)
        )

# Example usage (if needed)
if __name__ == "__main__":
    # This is where you'd initialize your Spring-like context and run the application
    pass
