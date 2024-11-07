import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import RuleType
from .model import RuleModel

class RuleQuery(graphene.ObjectType):
    rule = graphene.Field(RuleType, uid=graphene.String(required=True))
    allRule = graphene.List(RuleType)

    def resolve_rule(self, info, uid):
        query = RuleType.get_query(info)
        return query.filter(RuleModel.uid == uid).first()

    def resolve_allRule(self, info):
        query = RuleType.get_query(info)
        return query.all()
