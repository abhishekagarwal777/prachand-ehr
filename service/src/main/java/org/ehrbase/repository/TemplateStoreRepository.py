import uuid
import io
import xml.etree.ElementTree as ET
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class InternalServerException(Exception):
    pass

class ObjectNotFoundException(Exception):
    pass

class TemplateMetaData:
    def __init__(self):
        self.operational_template = None
        self.internal_id = None
        self.created_on = None

class OPERATIONALTEMPLATE:
    def __init__(self, template_id: str, content: str):
        self.template_id = template_id
        self.content = content

    def getTemplateId(self):
        return self.template_id

    def xmlText(self):
        return self.content

Base = declarative_base()

class TemplateStoreRecord(Base):
    __tablename__ = 'template_store'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(String, unique=True)
    content = Column(String)
    creation_time = Column(DateTime)

class TemplateStoreRepository:
    def __init__(self, session: Session, time_provider):
        self.session = session
        self.time_provider = time_provider

    def store(self, operational_template: OPERATIONALTEMPLATE):
        template_store_record = TemplateStoreRecord()
        self.set_template(operational_template, template_store_record, lambda rec: setattr(rec, 'id', uuid.uuid4()))
        template_store_record.creation_time = self.time_provider.get_now()
        self.session.add(template_store_record)
        self.session.commit()

    def update(self, operational_template: OPERATIONALTEMPLATE):
        template_id = operational_template.getTemplateId()
        template_store_record = self.session.query(TemplateStoreRecord).filter(TemplateStoreRecord.template_id == template_id).one_or_none()
        
        if not template_store_record:
            raise ObjectNotFoundException("OPERATIONALTEMPLATE", f"No template with id = {template_id}")

        self.set_template(operational_template, template_store_record, lambda rec: setattr(rec, 'id', rec.id))
        template_store_record.creation_time = self.time_provider.get_now()
        self.session.commit()

    def find_all(self) -> List[TemplateMetaData]:
        results = self.session.query(TemplateStoreRecord).all()
        return [self.build_metadata(record) for record in results]

    def find_all_template_ids(self) -> List[str]:
        return self.session.query(TemplateStoreRecord.template_id).all()

    def build_metadata(self, record: TemplateStoreRecord) -> TemplateMetaData:
        template_meta_data = TemplateMetaData()
        template_meta_data.operational_template = self.build_operational_template(record.content)
        template_meta_data.internal_id = record.id
        template_meta_data.created_on = record.creation_time
        return template_meta_data

    def delete(self, template_id: str):
        result = self.session.query(TemplateStoreRecord).filter(TemplateStoreRecord.template_id == template_id).delete()
        if result == 0:
            raise ObjectNotFoundException("OPERATIONALTEMPLATE", f"No template with id = {template_id}")
        self.session.commit()

    def find_by_template_id(self, template_id: str) -> Optional[OPERATIONALTEMPLATE]:
        result = self.session.query(TemplateStoreRecord.content).filter(TemplateStoreRecord.template_id == template_id).one_or_none()
        if result:
            return self.build_operational_template(result[0])
        return None

    def find_template_id_by_uuid(self, uuid: uuid.UUID) -> Optional[str]:
        result = self.session.query(TemplateStoreRecord.template_id).filter(TemplateStoreRecord.id == uuid).one_or_none()
        return result[0] if result else None

    def find_uuid_by_template_id(self, template_id: str) -> Optional[uuid.UUID]:
        result = self.session.query(TemplateStoreRecord.id).filter(TemplateStoreRecord.template_id == template_id).one_or_none()
        return result[0] if result else None

    def build_operational_template(self, content: str) -> OPERATIONALTEMPLATE:
        try:
            tree = ET.ElementTree(ET.fromstring(content))
            template_id = tree.getroot().attrib['templateId']
            return OPERATIONALTEMPLATE(template_id=template_id, content=content)
        except ET.ParseError as e:
            raise InternalServerException(str(e))

    def set_template(self, template: OPERATIONALTEMPLATE, template_store_record: TemplateStoreRecord, set_id):
        set_id(template_store_record)
        template_store_record.template_id = template.getTemplateId()
        template_store_record.content = template.xmlText()
