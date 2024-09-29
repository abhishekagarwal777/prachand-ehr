from bidict import bidict
from typing import Optional


class ContributionChangeType:
    CREATION = "creation"
    AMENDMENT = "amendment"
    MODIFICATION = "modification"
    SYNTHESIS = "synthesis"
    UNKNOWN = "unknown"
    DELETED = "deleted"


class ChangeTypeUtils:
    JOOQ_CHANGE_TYPE_TO_CODE = bidict({
        ContributionChangeType.CREATION: "249",
        ContributionChangeType.AMENDMENT: "250",
        ContributionChangeType.MODIFICATION: "251",
        ContributionChangeType.SYNTHESIS: "252",
        ContributionChangeType.UNKNOWN: "253",
        ContributionChangeType.DELETED: "523",
    })

    @staticmethod
    def get_jooq_change_type_by_code(code: Optional[str]) -> Optional[str]:
        return ChangeTypeUtils.JOOQ_CHANGE_TYPE_TO_CODE.inverse.get(code)

    @staticmethod
    def get_code_by_jooq_change_type(cct: Optional[str]) -> Optional[str]:
        return ChangeTypeUtils.JOOQ_CHANGE_TYPE_TO_CODE.get(cct)
