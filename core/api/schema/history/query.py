import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import ExternalRepoHistoryType, ExternalViewHistoryType, ExternalAlertHistoryType, ExternalFieldHistoryType, ExternalActionHistoryType

class ExternalQuery(graphene.ObjectType):
    externalRepoHistory = graphene.Field(ExternalRepoHistoryType, id=graphene.String(required=True))
    allExternalRepoHistory = graphene.List(ExternalRepoHistoryType)

    externalViewHistory = graphene.Field(ExternalViewHistoryType, id=graphene.String(required=True))
    allExternalViewHistory = graphene.List(ExternalViewHistoryType)

    externalAlertHistory = graphene.Field(ExternalAlertHistoryType, id=graphene.String(required=True))
    allExternalAlertHistory = graphene.List(ExternalAlertHistoryType)

    externalFieldHistory = graphene.Field(ExternalFieldHistoryType, id=graphene.String(required=True))
    allExternalFieldHistory = graphene.List(ExternalFieldHistoryType)

    externalActionHistory = graphene.Field(ExternalActionHistoryType, id=graphene.String(required=True))
    allExternalActionHistory = graphene.List(ExternalActionHistoryType)

    def resolve_externalRepoHistory(self, info, id):
        return ExternalRepoType.get_query(info).filter_by(id=id).first()

    def resolve_allExternalRepoHistory(self, info):
        return ExternalRepoType.get_query(info).all()

    def resolve_externalViewHistory(self, info, id):
        return ExternalViewType.get_query(info).filter_by(id=id).first()

    def resolve_allExternalViewHistory(self, info):
        return ExternalViewType.get_query(info).all()

    def resolve_externalAlertHistory(self, info, id):
        return ExternalAlertType.get_query(info).filter_by(id=id).first()

    def resolve_allExternalAlertHistory(self, info):
        return ExternalAlertType.get_query(info).all()

    def resolve_externalFieldHistory(self, info, id):
        return ExternalFieldType.get_query(info).filter_by(id=id).first()

    def resolve_allExternalFieldHistory(self, info):
        return ExternalFieldType.get_query(info).all()

    def resolve_externalActionHistory(self, info, id):
        return ExternalActionType.get_query(info).filter_by(id=id).first()

    def resolve_allExternalActionHistory(self, info):
        return ExternalActionType.get_query(info).all()
