from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

Base = declarative_base()

# Define database tables as classes
class Users(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)
    username = Column(String)

class PartyProxyRepository:
    SECURITY_USER_TYPE = "EHRbase Security Authentication User"
    EHRBASE = "EHRbase"

    def __init__(self, session: Session):
        self.session = session

    def find_internal_user_id(self, username: str) -> Optional[UUID]:
        result = self.session.execute(
            select(Users.id).where(Users.username == username)
        ).fetchone()
        return result[0] if result else None

    def create_internal_user(self, username: str) -> UUID:
        uuid = UUID()  # This should be replaced with a UUID generator
        user_record = Users(id=uuid, username=username)
        self.session.add(user_record)
        self.session.commit()
        return uuid

    def from_user(self, user_id: UUID) -> PartyIdentified:
        result = self.session.execute(
            select(Users.username).where(Users.id == user_id)
        ).fetchone()
        username = result[0] if result else None

        if username is None:
            raise Exception("User not found")

        identifier = DvIdentifier(
            id=username,
            issuer=self.EHRBASE,
            assigner=self.EHRBASE,
            type=self.SECURITY_USER_TYPE
        )

        external_ref = PartyRef(GenericId(user_id.hex, "DEMOGRAPHIC"), "User", "PARTY")
        party_identified = PartyIdentified(
            external_ref,
            f"EHRbase Internal {username}",
            [identifier]
        )

        return party_identified
