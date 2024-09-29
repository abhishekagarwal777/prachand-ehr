from typing import Any, Optional

class EhrStatus:
    def __init__(self, uid: str, archetype_node_id: str, name: str,
                 archetype_details: Any, feeder_audit: Any, subject: Any,
                 queryable: bool, modifiable: bool, other_details: Any):
        self.uid = uid
        self.archetype_node_id = archetype_node_id
        self.name = name
        self.archetype_details = archetype_details
        self.feeder_audit = feeder_audit
        self.subject = subject
        self.queryable = queryable
        self.modifiable = modifiable
        self.other_details = other_details

class EhrStatusDto:
    def __init__(self, uid: str, archetype_node_id: str, name: str,
                 archetype_details: Any, feeder_audit: Any, subject: Any,
                 queryable: bool, modifiable: bool, other_details: Any):
        self._uid = uid
        self._archetype_node_id = archetype_node_id
        self._name = name
        self._archetype_details = archetype_details
        self._feeder_audit = feeder_audit
        self._subject = subject
        self._queryable = queryable
        self._modifiable = modifiable
        self._other_details = other_details

    def uid(self) -> str:
        return self._uid

    def archetypeNodeId(self) -> str:
        return self._archetype_node_id

    def name(self) -> str:
        return self._name

    def archetypeDetails(self) -> Any:
        return self._archetype_details

    def feederAudit(self) -> Any:
        return self._feeder_audit

    def subject(self) -> Any:
        return self._subject

    def isQueryable(self) -> bool:
        return self._queryable

    def isModifiable(self) -> bool:
        return self._modifiable

    def otherDetails(self) -> Any:
        return self._other_details

class EhrStatusMapper:

    @staticmethod
    def to_dto(ehr_status: EhrStatus) -> EhrStatusDto:
        """
        Mapping of archi EhrStatus to EhrStatusDto.

        :param ehr_status: archi EhrStatus to map
        :return: EhrStatusDto
        """
        return EhrStatusDto(
            uid=ehr_status.uid,
            archetype_node_id=ehr_status.archetype_node_id,
            name=ehr_status.name,
            archetype_details=ehr_status.archetype_details,
            feeder_audit=ehr_status.feeder_audit,
            subject=ehr_status.subject,
            queryable=ehr_status.queryable,
            modifiable=ehr_status.modifiable,
            other_details=ehr_status.other_details
        )

    @staticmethod
    def from_dto(dto: EhrStatusDto) -> EhrStatus:
        """
        Mapping of EhrStatusDto to archi EhrStatus.

        :param dto: EhrStatusDto to map
        :return: EhrStatus
        """
        return EhrStatus(
            uid=dto.uid(),
            archetype_node_id=dto.archetypeNodeId(),
            name=dto.name(),
            archetype_details=dto.archetypeDetails(),
            feeder_audit=dto.feederAudit(),
            subject=dto.subject(),
            queryable=dto.isQueryable(),
            modifiable=dto.isModifiable(),
            other_details=dto.otherDetails()
        )
