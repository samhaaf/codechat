import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import TagType, RepoTagType, RuleTagType, FieldTagType

class TagQuery(graphene.ObjectType):
    tag = graphene.Field(TagType, uid=graphene.String(required=True))
    allTag = graphene.List(TagType)

    repoTag = graphene.Field(RepoTagType, uid=graphene.String(required=True))
    allRepoTag = graphene.List(RepoTagType)

    ruleTag = graphene.Field(RuleTagType, uid=graphene.String(required=True))
    allRuleTag = graphene.List(RuleTagType)

    fieldTag = graphene.Field(FieldTagType, uid=graphene.String(required=True))
    allFieldTag = graphene.List(FieldTagType)

    def resolve_tag(self, info, uid):
        return TagType.get_query(info).filter_by(uid=uid).first()

    def resolve_allTag(self, info):
        return TagType.get_query(info).all()

    def resolve_repoTag(self, info, uid):
        return RepoTagType.get_query(info).filter_by(uid=uid).first()

    def resolve_allRepoTag(self, info):
        return RepoTagType.get_query(info).all()

    def resolve_ruleTag(self, info, uid):
        return RuleTagType.get_query(info).filter_by(uid=uid).first()

    def resolve_allRuleTag(self, info):
        return RuleTagType.get_query(info).all()

    def resolve_fieldTag(self, info, uid):
        return FieldTagType.get_query(info).filter_by(uid=uid).first()

    def resolve_allFieldTag(self, info):
        return FieldTagType.get_query(info).all()
