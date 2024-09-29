from abc import ABC, abstractmethod

class AnnotationAspect(ABC):
    @abstractmethod
    def match_annotations(self):
        """ Return the list of annotations to match """
        pass

    @abstractmethod
    def action(self, func, *args, **kwargs):
        """ Perform an action at the join point (method invocation) """
        pass

from functools import wraps

class SecurityAspect(AnnotationAspect):
    def match_annotations(self):
        # Define the annotations this aspect cares about
        return ['ehrbase_security']

    def action(self, func, *args, **kwargs):
        print("Security aspect: Checking security before proceeding...")
        result = func(*args, **kwargs)  # Proceed with the original function
        print("Security aspect: Security check completed.")
        return result


def apply_aspect(aspect: AnnotationAspect):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if the method should be intercepted
            if aspect.match_annotations():
                return aspect.action(func, *args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator

security_aspect = SecurityAspect()

@apply_aspect(security_aspect)
def some_method():
    print("Executing some method")

# When you call the method, the security aspect will be applied
some_method()
