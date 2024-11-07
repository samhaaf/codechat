from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from api.db import Base

class UserModel(Base):
    __tablename__ = 'user'

    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
