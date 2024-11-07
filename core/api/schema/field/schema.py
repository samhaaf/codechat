import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .model import FieldModel

class FieldType(SQLAlchemyObjectType):
    class Meta:
        model = FieldModel
        interfaces = (graphene.relay.Node, )
