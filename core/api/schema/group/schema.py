import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .model import GroupModel, UserGroupModel

class GroupType(SQLAlchemyObjectType):
    class Meta:
        model = GroupModel
        interfaces = (graphene.relay.Node, )

    users = graphene.List('api.schema.user.schema.UserType')

class UserGroupType(SQLAlchemyObjectType):
    class Meta:
        model = UserGroupModel
        interfaces = (graphene.relay.Node, )
