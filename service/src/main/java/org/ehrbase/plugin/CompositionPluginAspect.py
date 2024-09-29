from typing import Optional, Callable, TypeVar
from uuid import UUID
from aspectlib import Aspect
from abc import ABC
import inspect

# Define type variables for generics
CompositionExtensionPoint = TypeVar('CompositionExtensionPoint')
Composition = TypeVar('Composition')
ObjectVersionId = TypeVar('ObjectVersionId')

class CompositionWithEhrId:
    def __init__(self, composition: Composition, ehr_id: UUID):
        self.composition = composition
        self.ehr_id = ehr_id

class CompositionWithEhrIdAndPreviousVersion:
    def __init__(self, composition: Composition, previous_version: ObjectVersionId, ehr_id: UUID):
        self.composition = composition
        self.previous_version = previous_version
        self.ehr_id = ehr_id

class CompositionVersionIdWithEhrId:
    def __init__(self, version_id: ObjectVersionId, ehr_id: UUID):
        self.version_id = version_id
        self.ehr_id = ehr_id

class CompositionIdWithVersionAndEhrId:
    def __init__(self, ehr_id: UUID, composition_id: UUID, version: int):
        self.ehr_id = ehr_id
        self.composition_id = composition_id
        self.version = version

class CompositionPluginAspect(AbstractPluginAspect[CompositionExtensionPoint], ABC):
    def __init__(self, bean_factory: ListableBeanFactory):
        super().__init__(bean_factory, CompositionExtensionPoint)

    @Aspect
    def around_create_composition(self, pjp):
        return Optional.of(self.proceed_with_plugin_extension_points(
            pjp,
            CompositionExtensionPoint.around_creation,
            lambda args: CompositionWithEhrId(args[1], args[0]),
            lambda i, args: [i.get_ehr_id(), i.get_composition()],
            lambda ret: ret or raise ValueError("Expected UUID not found")
        ))

    @Aspect
    def around_update_composition(self, pjp):
        return Optional.of(self.proceed_with_plugin_extension_points(
            pjp,
            CompositionExtensionPoint.around_update,
            lambda args: CompositionWithEhrIdAndPreviousVersion(args[2], args[1], args[0]),
            lambda i, args: [i.get_ehr_id(), i.get_previous_version(), i.get_composition()],
            lambda ret: ret or raise ValueError("Expected UUID not found")
        ))

    @Aspect
    def around_delete_composition(self, pjp):
        self.proceed_with_plugin_extension_points(
            pjp,
            CompositionExtensionPoint.around_delete,
            lambda args: CompositionVersionIdWithEhrId(args[1], args[0]),
            lambda i, args: [i.get_ehr_id(), i.get_version_id()],
            lambda _: None  # No return value for delete
        )

    @Aspect
    def around_retrieve_composition(self, pjp):
        return self.proceed_with_plugin_extension_points(
            pjp,
            CompositionExtensionPoint.around_retrieve,
            lambda args: CompositionIdWithVersionAndEhrId(args[0], args[1], args[2]),
            lambda i, args: [i.get_ehr_id(), i.get_composition_id(), i.get_version()]
        )

# Example instantiation for testing
if __name__ == "__main__":
    bean_factory = ListableBeanFactory()
    aspect = CompositionPluginAspect(bean_factory)
    print("CompositionPluginAspect initialized.")
