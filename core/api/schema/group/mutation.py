from graphene_sqlalchemy import SQLAlchemyMutation
from .model import GroupModel, UserGroupModel
from .schema import GroupType, UserGroupType
from api.db import db_session

class CreateGroup(SQLAlchemyMutation):
    class Meta:
        model = GroupModel
        type_ = GroupType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        group = GroupModel(**kwargs)
        db_session.add(group)
        db_session.commit()
        return cls(group)

class UpdateGroup(SQLAlchemyMutation):
    class Meta:
        model = GroupModel
        type_ = GroupType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        group = GroupModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(group, key, value)
        db_session.commit()
        return cls(group)

class DeleteGroup(SQLAlchemyMutation):
    class Meta:
        model = GroupModel
        type_ = GroupType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        group = GroupModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(group)
        db_session.commit()
        return cls(group)

class CreateUserGroup(SQLAlchemyMutation):
    class Meta:
        model = UserGroupModel
        type_ = UserGroupType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user_group = UserGroupModel(**kwargs)
        db_session.add(user_group)
        db_session.commit()
        return cls(user_group)

class UpdateUserGroup(SQLAlchemyMutation):
    class Meta:
        model = UserGroupModel
        type_ = UserGroupType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user_group = UserGroupModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(user_group, key, value)
        db_session.commit()
        return cls(user_group)

class DeleteUserGroup(SQLAlchemyMutation):
    class Meta:
        model = UserGroupModel
        type_ = UserGroupType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user_group = UserGroupModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(user_group)
        db_session.commit()
        return cls(user_group)

class GroupMutation(graphene.ObjectType):
    create_group = CreateGroup.Field()
    update_group = UpdateGroup.Field()
    delete_group = DeleteGroup.Field()

    create_user_group = CreateUserGroup.Field()
    update_user_group = UpdateUserGroup.Field()
    delete_user_group = DeleteUserGroup.Field()
