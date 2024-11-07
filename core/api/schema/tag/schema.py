import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .model import TagModel, RepoTagModel, RuleTagModel, FieldTagModel

class TagType(SQLAlchemyObjectType):
    class Meta:
        model = TagModel

    repos = graphene.List('api.schema.repo.schema.RepoType')
    rules = graphene.List('api.schema.rule.schema.RuleType')
    fields = graphene.List('api.schema.field.schema.FieldType')

class RepoTagType(SQLAlchemyObjectType):
    class Meta:
        model = RepoTagModel

class RuleTagType(SQLAlchemyObjectType):
    class Meta:
        model = RuleTagModel

class FieldTagType(SQLAlchemyObjectType):
    class Meta:
        model = FieldTagModel
