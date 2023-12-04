from typing import Collection, Union

from graphene import ObjectType
from graphene import Schema as GrapheneSchema
from graphql import GraphQLDirective

from .schema import Schema


def build_schema(
    query: Union[ObjectType, None] = None,
    mutation: Union[ObjectType, None] = None,
    directives: Union[Collection[GraphQLDirective], None] = None,
    **kwargs: dict,
) -> GrapheneSchema:
    schema = Schema(query=query, mutation=mutation, directives=directives, **kwargs)
    schema.auto_camelcase = kwargs.get("auto_camelcase", True)
    return schema
