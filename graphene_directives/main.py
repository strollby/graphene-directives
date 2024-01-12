from typing import Collection, Type, Union

import graphene
from graphene import Schema as GrapheneSchema
from graphql import GraphQLDirective

from . import DirectiveValidationError
from .data_models import SchemaDirective
from .schema import Schema


def build_schema(
    query: Union[graphene.ObjectType, Type[graphene.ObjectType]] = None,
    mutation: Union[graphene.ObjectType, Type[graphene.ObjectType]] = None,
    subscription: Union[graphene.ObjectType, Type[graphene.ObjectType]] = None,
    types: Collection[Union[graphene.ObjectType, Type[graphene.ObjectType]]] = None,
    directives: Union[Collection[GraphQLDirective], None] = None,
    auto_camelcase: bool = True,
    schema_directives: Collection[SchemaDirective] = None,
) -> GrapheneSchema:
    _schema_directive_set: set[str] = set()
    for schema_directive in schema_directives or []:
        if schema_directive.target_directive.name in _schema_directive_set:
            if not schema_directive.target_directive.is_repeatable:
                raise DirectiveValidationError(
                    f"{schema_directive.target_directive} is not repeatable on schema"
                )
        else:
            _schema_directive_set.add(schema_directive.target_directive.name)

    return Schema(
        query=query,
        mutation=mutation,
        subscription=subscription,
        types=types,
        directives=directives,
        auto_camelcase=auto_camelcase,
        schema_directives=schema_directives,
    )
