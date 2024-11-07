import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .model import ExternalRepoHistoryModel, ExternalViewHistoryModel, ExternalAlertHistoryModel, ExternalFieldHistoryModel, ExternalActionHistoryModel

class ExternalRepoHistoryType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalRepoHistoryModel
        interfaces = (graphene.relay.Node, )

class ExternalViewHistoryType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalViewHistoryModel
        interfaces = (graphene.relay.Node, )

class ExternalAlertHistoryType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalAlertHistoryModel
        interfaces = (graphene.relay.Node, )

class ExternalFieldHistoryType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalFieldHistoryModel
        interfaces = (graphene.relay.Node, )

class ExternalActionHistoryType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalActionHistoryModel
        interfaces = (graphene.relay.Node, )
