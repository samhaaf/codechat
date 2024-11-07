from graphene import Mutation, Argument, Field, InputObjectType
from sqlalchemy.inspection import inspect
from sqlalchemy import String, Integer
import graphene

class SQLAlchemyMutation(Mutation):
    @classmethod
    def __init_subclass_with_meta__(
            cls,
            model=None,
            create=False,
            delete=False,
            registry=None,
            arguments=None,
            only_fields=(),
            structure: Type[Structure] = None,
            exclude_fields=(),
            **options,
    ):
        meta = SQLAlchemyMutationOptions(cls)
        meta.create = create
        meta.model = model
        meta.delete = delete

        if arguments is None and not hasattr(cls, "Arguments"):
            arguments = {}
            # don't include id argument on create
            if not meta.create:
                arguments["id"] = ID(required=True)

            # don't include input argument on delete
            if not meta.delete:
                inputMeta = type(
                    "Meta",
                    (object,),
                    {
                        "model": model,
                        "exclude_fields": exclude_fields,
                        "only_fields": only_fields,
                    },
                )
                inputType = type(
                    cls.__name__ + "Input",
                    (SQLAlchemyInputObjectType,),
                    {"Meta": inputMeta},
                )
                arguments = {"input": inputType(required=True)}
        if not registry:
            registry = get_global_registry()
        output_type: ObjectType = registry.get_type_for_model(model)
        if structure:
            output_type = structure(output_type)
        super(SQLAlchemyMutation, cls).__init_subclass_with_meta__(
            _meta=meta, output=output_type, arguments=arguments, **options
        )

    @classmethod
    def mutate(cls, root, info, **kwargs):
        session = get_session(info.context)
        with session.no_autoflush:
            meta = cls._meta

            if meta.create:
                model = meta.model(**kwargs["input"])
                session.add(model)
            else:
                model = (
                    session.query(meta.model)
                        .filter(meta.model.id == kwargs["id"])
                        .first()
                )
            if meta.delete:
                session.delete(model)
            else:

                def setModelAttributes(model, attrs):
                    relationships = model.__mapper__.relationships
                    for key, value in attrs.items():
                        if key in relationships:
                            if getattr(model, key) is None:
                                # instantiate class of the same type as
                                # the relationship target
                                setattr(model, key, relationships[key].mapper.entity())
                            setModelAttributes(getattr(model, key), value)
                        else:
                            setattr(model, key, value)

                setModelAttributes(model, kwargs["input"])
            session.flush()  # session.commit() now throws session state exception: 'already committed'

            return model

    @classmethod
    def Field(cls, *args, **kwargs):
        return Field(
            cls._meta.output, args=cls._meta.arguments, resolver=cls._meta.resolver
        )
