import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from .schema import ExternalRepoType, ExternalViewType, ExternalAlertType, ExternalFieldType, ExternalActionType

class ExternalQuery(graphene.ObjectType):
    externalRepo = graphene.Field(ExternalRepoType, id=graphene.String(required=True))
    allExternalRepos = graphene.List(ExternalRepoType)

    externalView = graphene.Field(ExternalViewType, id=graphene.String(required=True))
    allExternalViews = graphene.List(ExternalViewType)

    externalAlert = graphene.Field(ExternalAlertType, id=graphene.String(required=True))
    allExternalAlerts = graphene.List(ExternalAlertType)

    externalField = graphene.Field(ExternalFieldType, ext_alert_id=graphene.String(required=True))
    allExternalFields = graphene.List(ExternalFieldType)

    externalAction = graphene.Field(ExternalActionType, ext_alert_id=graphene.String(required=True))
    allExternalActions = graphene.List(ExternalActionType)

    def resolve_externalRepo(self, info, id):
        return ExternalRepoType.get_query(info).filter_by(id=id).first()

    def resolve_allExternalRepos(self, info):
        print('Querying for allExternalRepos..')
        result = ExternalRepoType.get_query(info).all()
        print('Query returned:', result)
        return result

    def resolve_externalView(self, info, id):
        return ExternalViewType.get_query(info).filter_by(id=id).first()

    def resolve_allExternalViews(self, info):
        return ExternalViewType.get_query(info).all()

    def resolve_externalAlert(self, info, id):
        return ExternalAlertType.get_query(info).filter_by(id=id).first()

    def resolve_allExternalAlerts(self, info):
        return ExternalAlertType.get_query(info).all()

    def resolve_externalField(self, info, ext_alert_id):
        return ExternalFieldType.get_query(info).filter_by(ext_alert_id=ext_alert_id).first()

    def resolve_allExternalFields(self, info):
        return ExternalFieldType.get_query(info).all()

    def resolve_externalAction(self, info, ext_alert_id):
        return ExternalActionType.get_query(info).filter_by(ext_alert_id=ext_alert_id).first()

    def resolve_allExternalActions(self, info):
        return ExternalActionType.get_query(info).all()
