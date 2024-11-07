import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .model import RepoModel

class RepoType(SQLAlchemyObjectType):
    class Meta:
        model = RepoModel
        interfaces = (graphene.relay.Node, )
