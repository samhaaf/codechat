import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import UserType

class UserQuery(graphene.ObjectType):
    user = graphene.Field(UserType, uid=graphene.String(required=True))
    allUser = graphene.List(UserType)

    def resolve_user(self, info, uid):
        return UserType.get_query(info).filter_by(uid=uid).first()

    def resolve_allUser(self, info):
        return UserType.get_query(info).all()
