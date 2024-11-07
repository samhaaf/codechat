from sqlalchemy import Column, DateTime, func, ForeignKey, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from api.db import Base
from sqlalchemy.orm import relationship

class FieldModel(Base):
    __tablename__ = 'field'

    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    insert_datetime = Column(DateTime(timezone=True), server_default=func.now())
    update_datetime = Column(DateTime(timezone=True), onupdate=func.now())
    rule_uid = Column(UUID(as_uuid=True), ForeignKey('rule.uid'), nullable=False)
    field = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)

    rule = relationship("RuleModel", backref="fields")
