import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from .model import ExternalRepoModel, ExternalViewModel, ExternalAlertModel, ExternalFieldModel, ExternalActionModel

class ExternalRepoType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalRepoModel
        interfaces = (graphene.relay.Node, )

class ExternalViewType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalViewModel
        interfaces = (graphene.relay.Node, )

class ExternalAlertType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalAlertModel
        interfaces = (graphene.relay.Node, )

class ExternalFieldType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalFieldModel
        interfaces = (graphene.relay.Node, )

class ExternalActionType(SQLAlchemyObjectType):
    class Meta:
        model = ExternalActionModel
        interfaces = (graphene.relay.Node, )
