import graphene
from .access.mutation import AccessMutation
from .field.mutation import FieldMutation
from .group.mutation import GroupMutation
from .repo.mutation import RepoMutation
from .rule.mutation import RuleMutation
from .tag.mutation import TagMutation
from .user.mutation import UserMutation

class Mutation(
    AccessMutation,
    FieldMutation,
    GroupMutation,
    RepoMutation,
    RuleMutation,
    TagMutation,
    UserMutation,
    graphene.ObjectType
):
    pass
