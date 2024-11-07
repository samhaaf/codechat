from sqlalchemy import Column, String, DateTime, func, Boolean, ForeignKey, Integer, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from api.db import Base
from api.schema.repo.model import RepoModel

class RuleModel(Base):
    __tablename__ = 'rule'

    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    insert_datetime = Column(DateTime(timezone=True), server_default=func.now())
    update_datetime = Column(DateTime(timezone=True), onupdate=func.now())
    delete_datetime = Column(DateTime(timezone=True), nullable=True)
    ext_alert_id = Column(String, nullable=True)
    query_string = Column(Text, nullable=False)
