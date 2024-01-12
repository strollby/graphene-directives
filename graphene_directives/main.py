from typing import Collection, Type, Union

import graphene
from graphene import Schema as GrapheneSchema
from graphql import GraphQLDirective

from .schema import Schema


def build_schema(
    query: Union[graphene.ObjectType, Type[graphene.ObjectType]] = None,
    mutation: Union[graphene.ObjectType, Type[graphene.ObjectType]] = None,
    subscription: Union[graphene.ObjectType, Type[graphene.ObjectType]] = None,
    types: Collection[Union[graphene.ObjectType, Type[graphene.ObjectType]]] = None,
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
