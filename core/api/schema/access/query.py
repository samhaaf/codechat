import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import AccessType

class AccessQuery(graphene.ObjectType):
    access = graphene.Field(AccessType, uid=graphene.String(required=True))
    allAccess = graphene.List(AccessType)

    def resolve_acess(self, info, uid):
        return AccessType.get_query(info).filter_by(uid=uid).first()

    def resolve_allAccess(self, info):
        return AccessType.get_query(info).all()
