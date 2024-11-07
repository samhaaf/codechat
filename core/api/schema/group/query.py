import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import GroupType, UserGroupType

class GroupQuery(graphene.ObjectType):
    group = graphene.Field(GroupType, uid=graphene.String(required=True))
    allGroup = graphene.List(GroupType)

    userGroup = graphene.Field(UserGroupType, uid=graphene.String(required=True))
    allUserGroup = graphene.List(UserGroupType)

    def resolve_group(self, info, uid):
        return GroupType.get_query(info).filter_by(uid=uid).first()

    def resolve_allGroup(self, info):
        return GroupType.get_query(info).all()

    def resolve_userGroup(self, info, uid):
        return UserGroupType.get_query(info).filter_by(uid=uid).first()

    def resolve_allUserGroup(self, info):
        return UserGroupType.get_query(info).all()
