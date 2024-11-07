import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import RepoType

class RepoQuery(graphene.ObjectType):
    repo = graphene.Field(RepoType, uid=graphene.String(required=True))
    allRepo = graphene.List(RepoType)

    def resolve_repo(self, info, uid):
        return RepoType.get_query(info).filter_by(uid=uid).first()

    def resolve_allRepo(self, info):
        return RepoType.get_query(info).all()
