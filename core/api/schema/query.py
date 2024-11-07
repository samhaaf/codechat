import graphene
from .external.query import ExternalQuery
from .repo.query import RepoQuery
from .rule.query import RuleQuery
from .field.query import FieldQuery
from .user.query import UserQuery
from .group.query import GroupQuery
from .tag.query import TagQuery
from .access.query import AccessQuery

class Query(
    ExternalQuery,
    RepoQuery,
    RuleQuery,
    FieldQuery,
    UserQuery,
    GroupQuery,
    TagQuery,
    AccessQuery,
    graphene.ObjectType
):
    pass
