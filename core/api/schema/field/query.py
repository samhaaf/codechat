import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import FieldType

class FieldQuery(graphene.ObjectType):
    field = graphene.Field(FieldType, uid=graphene.String(required=True))
    allField = graphene.List(FieldType)

    def resolve_field(self, info, uid):
        return FieldType.get_query(info).filter_by(uid=uid).first()

    def resolve_allField(self, info):
        return FieldType.get_query(info).all()
