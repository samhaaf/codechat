from graphene_sqlalchemy import SQLAlchemyMutation, SQLAlchemyObjectType
from .model import UserModel
from .schema import UserType
from api.db import db_session

class CreateUser(SQLAlchemyMutation):
    class Meta:
        model = UserModel
        type_ = UserType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = UserModel(**kwargs)
        db_session.add(user)
        db_session.commit()
        return cls(user)

class UpdateUser(SQLAlchemyMutation):
    class Meta:
        model = UserModel
        type_ = UserType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = UserModel.query.filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(user, key, value)
        db_session.commit()
        return cls(user)

class DeleteUser(SQLAlchemyMutation):
    class Meta:
        model = UserModel
        type_ = UserType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = UserModel.query.filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(user)
        db_session.commit()
        return cls(user)

class UserMutation(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        type_ = UserType

    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
