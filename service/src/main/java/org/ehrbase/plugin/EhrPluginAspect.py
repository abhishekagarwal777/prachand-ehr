from typing import Optional, Callable, TypeVar, Tuple
from uuid import UUID
from aspectlib import Aspect
from abc import ABC
import inspect

# Define type variables for generics
EhrExtensionPoint = TypeVar('EhrExtensionPoint')
EhrStatus = TypeVar('EhrStatus')

class EhrStatusWithEhrId:
    def __init__(self, ehr_status: EhrStatus, ehr_id: UUID):
        self.ehr_status = ehr_status
        self.ehr_id = ehr_id

class EhrStatusVersionRequestParameters:
    def __init__(self, ehr_id: UUID, ehr_status_id: UUID, ehr_status_version: int):
        self.ehr_id = ehr_id
        self.ehr_status_id = ehr_status_id
        self.ehr_status_version = ehr_status_version

class EhrPluginAspect(AbstractPluginAspect[EhrExtensionPoint], ABC):
    STATUS_WITH_ID_INPUT_FUNCTION: Callable[[Tuple], EhrStatusWithEhrId] = \
        lambda args: EhrStatusWithEhrId(args[1], args[0])

    STATUS_WITH_ID_SET_ARGS_FUNCTION: Callable[[EhrStatusWithEhrId, Tuple], Tuple] = \
        lambda i, args: (i.ehr_id, i.ehr_status)

    def __init__(self, bean_factory: ListableBeanFactory):
        super().__init__(bean_factory, EhrExtensionPoint)

    @Aspect
    def around_create_ehr(self, pjp):
        return self.proceed_with_plugin_extension_points(
            pjp,
            EhrExtensionPoint.around_creation,
            self.STATUS_WITH_ID_INPUT_FUNCTION,
            self.STATUS_WITH_ID_SET_ARGS_FUNCTION
        )

    @Aspect
    def around_update_ehr_status(self, pjp):
        return self.proceed_with_plugin_extension_points(
            pjp,
            EhrExtensionPoint.around_update,
            self.STATUS_WITH_ID_INPUT_FUNCTION,
            self.STATUS_WITH_ID_SET_ARGS_FUNCTION
        )

    @Aspect
    def around_retrieve_ehr_status_at_version(self, pjp):
        return self.proceed_with_plugin_extension_points(
            pjp,
            EhrExtensionPoint.around_retrieve_at_version,
            lambda args: EhrStatusVersionRequestParameters(args[0], args[1], args[2]),
            lambda i, args: (i.ehr_id, i.ehr_status_id, i.ehr_status_version)
        )

# Example instantiation for testing
if __name__ == "__main__":
    bean_factory = ListableBeanFactory()
    aspect = EhrPluginAspect(bean_factory)
    print("EhrPluginAspect initialized.")
