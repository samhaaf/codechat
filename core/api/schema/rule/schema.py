import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .model import RuleModel

class RuleType(SQLAlchemyObjectType):
    class Meta:
        model = RuleModel
        interfaces = (graphene.relay.Node, )
