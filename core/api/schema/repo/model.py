from sqlalchemy import Column, String, DateTime, func, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from api.db import Base

class RepoModel(Base):
    __tablename__ = 'repo'

    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    insert_datetime = Column(DateTime(timezone=True), server_default=func.now())
    update_datetime = Column(DateTime(timezone=True), onupdate=func.now())
    delete_datetime = Column(DateTime(timezone=True), nullable=True)
    ext_view_id = Column(String, nullable=True)
    ext_repo_id = Column(String, nullable=True)
    name = Column(String, unique=True, nullable=False)
    is_view = hybrid_property(lambda self: self.ext_view_id is not None)
