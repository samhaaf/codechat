import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .model import UserModel

class UserType(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (graphene.relay.Node, )
