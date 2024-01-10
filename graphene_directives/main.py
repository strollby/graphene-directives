from typing import Collection, Union

import graphene
from graphene import Schema as GrapheneSchema
from graphql import GraphQLDirective

from .schema import Schema


def build_schema(
    query: graphene.ObjectType = None,
    mutation: graphene.ObjectType = None,
    subscription: graphene.ObjectType = None,
    types: list[graphene.ObjectType] = None,
    directives: Union[Collection[GraphQLDirective], None] = None,
    auto_camelcase: bool = True,
) -> GrapheneSchema:
    return Schema(
        query=query,
        mutation=mutation,
        subscription=subscription,
        types=types,
        directives=directives,
        auto_camelcase=auto_camelcase,
    )
