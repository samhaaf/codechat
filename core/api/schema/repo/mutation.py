from graphene_sqlalchemy import SQLAlchemyMutation
from .model import RepoModel
from .schema import RepoType
from api.db import db_session

class CreateRepo(SQLAlchemyMutation):
    class Meta:
        model = RepoModel
        type_ = RepoType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        repo = RepoModel(**kwargs)
        db_session.add(repo)
        db_session.commit()
        return cls(repo)

class UpdateRepo(SQLAlchemyMutation):
    class Meta:
        model = RepoModel
        type_ = RepoType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        repo = RepoModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(repo, key, value)
        db_session.commit()
        return cls(repo)

class DeleteRepo(SQLAlchemyMutation):
    class Meta:
        model = RepoModel
        type_ = RepoType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        repo = RepoModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(repo)
        db_session.commit()
        return cls(repo)

class RepoMutation(graphene.ObjectType):
    create_repo = CreateRepo.Field()
    update_repo = UpdateRepo.Field()
    delete_repo = DeleteRepo.Field()
