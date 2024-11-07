from graphene_sqlalchemy import SQLAlchemyMutation
from .model import RuleModel
from .schema import RuleType
from api.db import db_session

class CreateRule(SQLAlchemyMutation):
    class Meta:
        model = RuleModel
        type_ = RuleType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        rule = RuleModel(**kwargs)
        db_session.add(rule)
        db_session.commit()
        return cls(rule)

class UpdateRule(SQLAlchemyMutation):
    class Meta:
        model = RuleModel
        type_ = RuleType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        rule = RuleModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(rule, key, value)
        db_session.commit()
        return cls(rule)

class DeleteRule(SQLAlchemyMutation):
    class Meta:
        model = RuleModel
        type_ = RuleType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        rule = RuleModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(rule)
        db_session.commit()
        return cls(rule)

class RuleMutation(graphene.ObjectType):
    create_rule = CreateRule.Field()
    update_rule = UpdateRule.Field()
    delete_rule = DeleteRule.Field()
