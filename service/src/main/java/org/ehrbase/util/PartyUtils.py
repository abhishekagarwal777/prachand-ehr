from typing import Optional, Union
from EHR import PartyProxy, PartyIdentified, PartySelf, PartyRelated, PartyRef  # Replace with actual imports
from EHR.exceptions import InternalServerException  # Replace with actual import

class PartyUtils:
    """
    Utility class for PartyProxy and its concrete implementations.
    """

    @staticmethod
    def is_empty(party_proxy: Optional[PartyProxy]) -> bool:
        if party_proxy is None:
            return True

        if PartyUtils.is_party_self(party_proxy):
            return PartyUtils.is_empty_party_self(party_proxy)  # Casting to PartySelf not needed in Python
        elif PartyUtils.is_party_identified(party_proxy):
            return PartyUtils.is_empty_party_identified(party_proxy)  # Casting to PartyIdentified not needed
        elif PartyUtils.is_party_related(party_proxy):
            return PartyUtils.is_empty_party_related(party_proxy)  # Casting to PartyRelated not needed
        else:
            raise InternalServerException(
                f"Unhandled Party type detected: {party_proxy.__class__.__name__}"
            )

    @staticmethod
    def is_empty_party_identified(party_identified: Optional[PartyIdentified]) -> bool:
        if party_identified is None:
            return True
        return (party_identified.name is None
                and not party_identified.identifiers
                and (party_identified.external_ref is None or PartyUtils.is_empty_party_ref(party_identified.external_ref)))

    @staticmethod
    def is_empty_party_self(party_self: Optional[PartySelf]) -> bool:
        if party_self is None:
            return True
        return party_self.external_ref is None or PartyUtils.is_empty_party_ref(party_self.external_ref)

    @staticmethod
    def is_empty_party_ref(party_ref: Optional[PartyRef]) -> bool:
        if party_ref is None:
            return True
        return (party_ref.id is None
                and party_ref.namespace is None
                and party_ref.type is None)

    @staticmethod
    def is_empty_party_related(party_related: Optional[PartyRelated]) -> bool:
        if party_related is None:
            return True
        return (party_related.name is None
                and not party_related.identifiers
                and party_related.relationship is None
                and (party_related.external_ref is None or PartyUtils.is_empty_party_ref(party_related.external_ref)))

    @staticmethod
    def is_party_self(party_proxy: PartyProxy) -> bool:
        return party_proxy.__class__.__name__ == "PartySelf"

    @staticmethod
    def is_party_identified(party_proxy: PartyProxy) -> bool:
        return party_proxy.__class__.__name__ == "PartyIdentified"

    @staticmethod
    def is_party_related(party_proxy: PartyProxy) -> bool:
        return party_proxy.__class__.__name__ == "PartyRelated"
