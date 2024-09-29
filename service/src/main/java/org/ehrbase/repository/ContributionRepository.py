import uuid
from typing import Optional
from sqlalchemy import select, insert, update, delete, JSON
from sqlalchemy.orm import Session
from datetime import datetime
from EHR.models import Contribution, AuditDetails  # Replace with actual model imports
from EHR.services import SystemService, UserService, PartyProxyRepository, TimeProvider
from EHR.exceptions import UnexpectedSwitchCaseException
from EHR.enums import ContributionChangeType, ContributionDataType  # Replace with actual enum imports

class ContributionRepository:
    def __init__(self, session: Session, system_service: SystemService,
                 user_service: UserService, party_proxy_repository: PartyProxyRepository,
                 time_provider: TimeProvider):
        self.session = session
        self.system_service = system_service
        self.user_service = user_service
        self.party_proxy_repository = party_proxy_repository
        self.time_provider = time_provider

    def create_default(self, ehr_id: uuid.UUID, contribution_type: ContributionDataType,
                       contribution_change_type: ContributionChangeType) -> uuid.UUID:
        audit_details_record_id = self.create_default_audit(contribution_change_type, "CONTRIBUTION")
        return self.create_contribution(ehr_id, uuid.uuid4(), contribution_type, audit_details_record_id)

    def create_default_audit(self, contribution_change_type: ContributionChangeType, target_type: str) -> uuid.UUID:
        audit_details_record = AuditDetails()
        audit_details_record.id = uuid.uuid4()
        audit_details_record.time_committed = self.time_provider.get_now()
        audit_details_record.target_type = target_type
        audit_details_record.committer = None
        audit_details_record.user_id = self.user_service.get_current_user_id()
        audit_details_record.change_type = contribution_change_type

        self.session.add(audit_details_record)
        self.session.commit()
        return audit_details_record.id

    def create_contribution(self, ehr_id: uuid.UUID, contribution_uuid: uuid.UUID,
                            contribution_type: ContributionDataType, audit_details_record_id: uuid.UUID) -> uuid.UUID:
        contribution_record = Contribution()
        contribution_record.ehr_id = ehr_id
        contribution_record.id = contribution_uuid
        contribution_record.contribution_type = contribution_type
        contribution_record.has_audit = audit_details_record_id

        self.session.add(contribution_record)
        self.session.commit()
        return contribution_record.id

    def create_audit(self, audit_details: dict, target_type: str) -> uuid.UUID:
        audit_details_record = AuditDetails()
        audit_details_record.id = uuid.uuid4()
        audit_details_record.time_committed = self.time_provider.get_now()

        if self.party_proxy_repository.from_user(self.user_service.get_current_user_id()) != audit_details['committer']:
            audit_details_record.committer = JSON.dumps(audit_details['committer'])

        audit_details_record.target_type = target_type
        audit_details_record.change_type = self.to(audit_details['change_type'])
        audit_details_record.description = audit_details.get('description', None)
        audit_details_record.user_id = self.user_service.get_current_user_id()

        self.session.add(audit_details_record)
        self.session.commit()
        return audit_details_record.id

    def to(self, change_type: dict) -> ContributionChangeType:
        code_string = change_type['defining_code']['code_string']
        if code_string == "249":
            return ContributionChangeType.CREATION
        elif code_string == "250":
            return ContributionChangeType.AMENDMENT
        elif code_string == "251":
            return ContributionChangeType.MODIFICATION
        elif code_string == "252":
            return ContributionChangeType.SYNTHESIS
        elif code_string == "253":
            return ContributionChangeType.UNKNOWN
        elif code_string == "523":
            return ContributionChangeType.DELETED
        else:
            raise UnexpectedSwitchCaseException(f"Unexpected change type: {change_type}")

    def find_by_id(self, contribution_id: uuid.UUID) -> Optional[Contribution]:
        stmt = select(Contribution).where(Contribution.id == contribution_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def find_audit_details(self, audit_id: uuid.UUID) -> dict:
        stmt = select(AuditDetails).where(AuditDetails.id == audit_id)
        audit_details_record = self.session.execute(stmt).scalar_one_or_none()

        if not audit_details_record:
            return None

        audit_details = {
            'system_id': self.system_service.get_system_id(),
            'committer': audit_details_record.committer or self.party_proxy_repository.from_user(audit_details_record.user_id),
            'description': audit_details_record.description,
            'change_type': {
                'code': audit_details_record.change_type.code,
                'description': audit_details_record.change_type.description
            },
            'time_committed': audit_details_record.time_committed
        }

        return audit_details
