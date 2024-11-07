from graphene_sqlalchemy import SQLAlchemyMutation
from .model import TagModel, RepoTagModel, RuleTagModel, FieldTagModel
from .schema import TagType, RepoTagType, RuleTagType, FieldTagType

class CreateTag(SQLAlchemyMutation):
    class Meta:
        model = TagModel
        type_ = TagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        tag = TagModel(**kwargs)
        db_session.add(tag)
        db_session.commit()
        return cls(tag)

class UpdateTag(SQLAlchemyMutation):
    class Meta:
        model = TagModel
        type_ = TagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        tag = TagModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(tag, key, value)
        db_session.commit()
        return cls(tag)

class DeleteTag(SQLAlchemyMutation):
    class Meta:
        model = TagModel
        type_ = TagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        tag = TagModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(tag)
        db_session.commit()
        return cls(tag)

class CreateRepoTag(SQLAlchemyMutation):
    class Meta:
        model = RepoTagModel
        type_ = RepoTagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        repo_tag = RepoTagModel(**kwargs)
        db_session.add(repo_tag)
        db_session.commit()
        return cls(repo_tag)

class UpdateRepoTag(SQLAlchemyMutation):
    class Meta:
        model = RepoTagModel
        type_ = RepoTagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        repo_tag = RepoTagModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(repo_tag, key, value)
        db_session.commit()
        return cls(repo_tag)

class DeleteRepoTag(SQLAlchemyMutation):
    class Meta:
        model = RepoTagModel
        type_ = RepoTagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        repo_tag = RepoTagModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(repo_tag)
        db_session.commit()
        return cls(repo_tag)

class CreateRuleTag(SQLAlchemyMutation):
    class Meta:
        model = RuleTagModel
        type_ = RuleTagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        rule_tag = RuleTagModel(**kwargs)
        db_session.add(rule_tag)
        db_session.commit()
        return cls(rule_tag)

class UpdateRuleTag(SQLAlchemyMutation):
    class Meta:
        model = RuleTagModel
        type_ = RuleTagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        rule_tag = RuleTagModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(rule_tag, key, value)
        db_session.commit()
        return cls(rule_tag)

class DeleteRuleTag(SQLAlchemyMutation):
    class Meta:
        model = RuleTagModel
        type_ = RuleTagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        rule_tag = RuleTagModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(rule_tag)
        db_session.commit()
        return cls(rule_tag)

class CreateFieldTag(SQLAlchemyMutation):
    class Meta:
        model = FieldTagModel
        type_ = FieldTagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        field_tag = FieldTagModel(**kwargs)
        db_session.add(field_tag)
        db_session.commit()
        return cls(field_tag)

class UpdateFieldTag(SQLAlchemyMutation):
    class Meta:
        model = FieldTagModel
        type_ = FieldTagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        field_tag = FieldTagModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(field_tag, key, value)
        db_session.commit()
        return cls(field_tag)

class DeleteFieldTag(SQLAlchemyMutation):
    class Meta:
        model = FieldTagModel
        type_ = FieldTagType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        field_tag = FieldTagModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(field_tag)
        db_session.commit()
        return cls(field_tag)
        
class TagMutation(graphene.ObjectType):
    create_tag = CreateTag.Field()
    update_tag = UpdateTag.Field()
    delete_tag = DeleteTag.Field()

    create_repo_tag = CreateRepoTag.Field()
    update_repo_tag = UpdateRepoTag.Field()
    delete_repo_tag = DeleteRepoTag.Field()

    create_rule_tag = CreateRuleTag.Field()
    update_rule_tag = UpdateRuleTag.Field()
    delete_rule_tag = DeleteRuleTag.Field()

    create_field_tag = CreateFieldTag.Field()
    update_field_tag = UpdateFieldTag.Field()
    delete_field_tag = DeleteFieldTag.Field()
