from graphene_sqlalchemy import SQLAlchemyMutation
from .model import FieldModel
from .schema import FieldType
import graphene

class CreateField(SQLAlchemyMutation):
    class Meta:
        model = FieldModel
        type_ = FieldType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        field = FieldModel(**kwargs)
        db_session.add(field)
        db_session.commit()
        return cls(field)

class UpdateField(SQLAlchemyMutation):
    class Meta:
        model = FieldModel
        type_ = FieldType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        field = FieldModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        for key, value in kwargs.items():
            setattr(field, key, value)
        db_session.commit()
        return cls(field)

class DeleteField(SQLAlchemyMutation):
    class Meta:
        model = FieldModel
        type_ = FieldType

    @classmethod
    def mutate(cls, root, info, **kwargs):
        field = FieldModel.get_query(info).filter_by(uid=kwargs.get('uid')).first()
        db_session.delete(field)
        db_session.commit()
        return cls(field)

class FieldMutation(graphene.ObjectType):
    create_field = CreateField.Field()
    update_field = UpdateField.Field()
    delete_field = DeleteField.Field()
