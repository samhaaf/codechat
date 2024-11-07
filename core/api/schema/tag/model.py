from sqlalchemy import Column, String, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import relationship
from api.db import Base
from api.schema.repo.model import RepoModel
from api.schema.rule.model import RuleModel
from api.schema.field.model import FieldModel

class TagModel(Base):
    __tablename__ = 'tag'
    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    key = Column(String, nullable=False)
    value = Column(String)
    is_enum = Column(Boolean, default=False)

class RepoTagModel(Base):
    __tablename__ = 'repo_tag'
    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    repo_uid = Column(UUID(as_uuid=True), ForeignKey('repo.uid'), nullable=False)
    tag_uid = Column(UUID(as_uuid=True), ForeignKey('tag.uid'), nullable=False)

RepoModel.tags = relationship(TagModel, secondary=RepoTagModel.__tablename__, backref='repos')


class RuleTagModel(Base):
    __tablename__ = 'rule_tag'
    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    rule_uid = Column(UUID(as_uuid=True), ForeignKey('rule.uid'), nullable=False)
    tag_uid = Column(UUID(as_uuid=True), ForeignKey('tag.uid'), nullable=False)

RuleModel.tags = relationship(TagModel, secondary=RuleTagModel.__tablename__, backref='rules')


class FieldTagModel(Base):
    __tablename__ = 'field_tag'
    uid = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    field_uid = Column(UUID(as_uuid=True), ForeignKey('field.uid'), nullable=False)
    tag_uid = Column(UUID(as_uuid=True), ForeignKey('tag.uid'), nullable=False)

FieldModel.tags = relationship(TagModel, secondary=FieldTagModel.__tablename__, backref='fields')
