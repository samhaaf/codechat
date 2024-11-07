from graphene_sqlalchemy import SQLAlchemyMutation
from .model import AccessModel  
from .schema import AccessType


class CreateAccess(SQLAlchemyMutation):
    class Meta:
        model = AccessModel
        type_ = AccessType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        access = AccessModel(**kwargs)
        db_session.add(access)
        db_session.commit()
        return cls(access)


class UpdateAccess(SQLAlchemyMutation):
    class Meta:
        model = AccessModel
        type_ = AccessType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        access = db_session.query(AccessModel).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(access, key, value)
        db_session.commit()
        return cls(access)


class DeleteAccess(SQLAlchemyMutation):
    class Meta:
        model = AccessModel
        type_ = AccessType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        access = db_session.query(AccessModel).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(access)
        db_session.commit()
        return cls(access)


class AccessMutation(graphene.ObjectType):
    create_access = CreateAccess.Field()
    update_access = UpdateAccess.Field()
    delete_access = DeleteAccess.Field()
