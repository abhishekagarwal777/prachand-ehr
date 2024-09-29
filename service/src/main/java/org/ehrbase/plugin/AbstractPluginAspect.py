from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, List, TypeVar, Dict, Any, Tuple
import inspect

# Define type variables for generics
EXTENSIONPOINT = TypeVar('EXTENSIONPOINT')
IN = TypeVar('IN')
OUT = TypeVar('OUT')

class InternalServerException(Exception):
    pass

class AnnotationAwareOrderComparator:
    @staticmethod
    def compare(obj1, obj2) -> int:
        # Placeholder for actual comparison logic based on @Order
        return (obj1.__class__.__name__ > obj2.__class__.__name__) - (obj1.__class__.__name__ < obj2.__class__.__name__)

class ListableBeanFactory:
    def __init__(self):
        self.beans: Dict[str, Any] = {}

    def register_bean(self, name: str, bean: Any):
        self.beans[name] = bean

    def get_beans_of_type(self, clazz: type) -> Dict[str, Any]:
        return {name: bean for name, bean in self.beans.items() if isinstance(bean, clazz)}

class AbstractPluginAspect(ABC):
    def __init__(self, bean_factory: ListableBeanFactory, clazz: type):
        self.bean_factory = bean_factory
        self.clazz = clazz

    @property
    def extension_points_comparator(self):
        return lambda e1, e2: (
            -1 if AnnotationAwareOrderComparator.compare(e1[1], e2[1]) > 0 else
            (1 if AnnotationAwareOrderComparator.compare(e1[1], e2[1]) < 0 else
             (0 if e1[0] < e2[0] else (1 if e1[0] > e2[0] else 0)))
            )
        )

    def proceed(self, pjp, args):
        try:
            return pjp.proceed(args)
        except (RuntimeError, Exception) as e:
            raise e  # Simple rethrow to handle in Controller layer
        except Exception as e:
            raise InternalServerException(str(e)) from e

    def get_active_extension_points_ordered_desc(self) -> List[EXTENSIONPOINT]:
        return sorted(
            self.bean_factory.get_beans_of_type(self.clazz).items(),
            key=self.extension_points_comparator
        )

    @abstractmethod
    def in_service_layer(self):
        """ Decorator to define pointcut in service layer """
        pass

    def proceed_with_plugin_extension_points(
            self,
            pjp,
            extension_point_method: Callable[[EXTENSIONPOINT, IN, Callable[[Any], OUT]], OUT],
            args_to_input_obj: Callable[[List[Any]], IN],
            set_args: Callable[[IN, List[Any]], List[Any]],
            after_proceed: Callable[[Any], OUT] = lambda ret: ret
    ) -> OUT:
        extension_points = self.get_active_extension_points_ordered_desc()
        if not extension_points:
            return after_proceed(self.proceed(pjp, pjp.get_args()))

        input_args_obj = args_to_input_obj(pjp.get_args())
        # Last extension point (first in the list) will hand over to the service layer
        call_chain = lambda in_arg: after_proceed(self.proceed(pjp, set_args(in_arg, pjp.get_args())))
        
        # Set up extension points to hand over to the next one of lower priority
        for ep in extension_points[:-1]:
            last_call = call_chain
            call_chain = lambda in_arg, ep=ep, last_call=last_call: extension_point_method(ep[1], in_arg, last_call)

        # Actually execute the first extension point method
        return extension_point_method(extension_points[-1][1], input_args_obj, call_chain)

# Example usage (Implementing an example subclass for demonstration purposes)
class ExampleExtensionPoint:
    pass

class ExamplePluginAspect(AbstractPluginAspect[ExampleExtensionPoint]):
    def in_service_layer(self):
        # Example pointcut implementation
        pass

# Example instantiation for testing
if __name__ == "__main__":
    bean_factory = ListableBeanFactory()
    aspect = ExamplePluginAspect(bean_factory, ExampleExtensionPoint)
    print("AbstractPluginAspect initialized.")
