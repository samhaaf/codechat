import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .model import AccessModel

class AccessType(SQLAlchemyObjectType):
    class Meta:
        model = AccessModel
        interfaces = (graphene.relay.Node, )
