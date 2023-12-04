from typing import Collection

from graphene import ObjectType, Schema
from graphql import GraphQLDirective

from .schema import _Schema


def build_schema(
    query: ObjectType | None = None,
    mutation: ObjectType | None = None,
    directives: Collection[GraphQLDirective] | None = None,
    **kwargs: dict,
) -> Schema:
    schema = _Schema(query=query, mutation=mutation, directives=directives, **kwargs)
    schema.auto_camelcase = kwargs.get("auto_camelcase", True)
    return schema
