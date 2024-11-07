from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class AccessModel(Base):
    __tablename__ = 'access'

    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    table_name = Column(String, nullable=False)
    user_uid = Column(UUID(as_uuid=True), nullable=True)
    group_uid = Column(UUID(as_uuid=True), nullable=True)
    and_conditions = Column(JSON, nullable=False)
    can_read = Column(Boolean, nullable=True)
    can_update = Column(Boolean, nullable=True)
    can_insert = Column(Boolean, nullable=True)
    can_delete = Column(Boolean, nullable=True)
