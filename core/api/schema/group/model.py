from sqlalchemy import Column, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from api.db import Base
from api.schema.user.model import UserModel


class GroupModel(Base):
    __tablename__ = 'group'

    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    name = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=True)


class UserGroupModel(Base):
    __tablename__ = 'user_group'

    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    user_uid = Column(UUID(as_uuid=True), ForeignKey('user.uid'), nullable=False)
    group_uid = Column(UUID(as_uuid=True), ForeignKey('group.uid'), nullable=False)

GroupModel.users = relationship(UserModel, secondary=UserGroupModel.__tablename__, backref='groups')
