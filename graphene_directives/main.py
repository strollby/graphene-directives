from typing import Union
from collections.abc import Collection

import graphene
from graphene import Schema as GrapheneSchema
from graphql import GraphQLDirective
from graphql import specified_directives

from . import DirectiveValidationError
from .data_models import SchemaDirective
from .schema import Schema


def build_schema(
    query: Union[graphene.ObjectType, type[graphene.ObjectType]] = None,
    mutation: Union[graphene.ObjectType, type[graphene.ObjectType]] = None,
    subscription: Union[graphene.ObjectType, type[graphene.ObjectType]] = None,
    types: Collection[Union[graphene.ObjectType, type[graphene.ObjectType]]] = None,
    directives: Union[Collection[GraphQLDirective], None] = None,
    auto_camelcase: bool = True,
    schema_directives: Collection[SchemaDirective] = None,
    include_graphql_spec_directives: bool = True,
) -> GrapheneSchema:
    """
    Build Schema.

    Args:
        query (type[ObjectType]): Root query *ObjectType*. Describes entry point for fields to *read*
            data in your Schema.
        mutation (Optional[type[ObjectType]]): Root mutation *ObjectType*. Describes entry point for
            fields to *create, update or delete* data in your API.
        subscription (Optional[type[ObjectType]]): Root subscription *ObjectType*. Describes entry point
            for fields to receive continuous updates.
        types (Optional[Collection[type[ObjectType]]]): List of any types to include in schema that
            may not be introspected through root types.
        directives (List[GraphQLDirective], optional): List of custom directives to include in the
            GraphQL schema.
        auto_camelcase (bool): Fieldnames will be transformed in Schema's TypeMap from snake_case
            to camelCase (preferred by GraphQL standard). Default True.
        schema_directives (Collection[SchemaDirective]): Directives that can be defined at DIRECTIVE_LOCATION.SCHEMA
            with their argument values.
        include_graphql_spec_directives (bool): Includes directives defined by GraphQL spec (@include, @skip,
            @deprecated, @specifiedBy)
    """

    _schema_directive_set: set[str] = set()
    for schema_directive in schema_directives or []:
        if schema_directive.target_directive.name in _schema_directive_set:
            if not schema_directive.target_directive.is_repeatable:
                raise DirectiveValidationError(
                    f"{schema_directive.target_directive} is not repeatable on schema"
                )
        else:
            _schema_directive_set.add(schema_directive.target_directive.name)

    directives = list(directives) if directives is not None else []

    _directive_set: set[str] = set()
    for directive in directives:
        if directive.name in _directive_set:
            raise DirectiveValidationError(f"Duplicate {directive} found")
        _directive_set.add(directive.name)

    # Validate if custom directive conflicts with graphql spec default directives
    _duplicate_default_directives = _directive_set.intersection(
        {directive.name for directive in specified_directives}
    )

    if _duplicate_default_directives:
        formatted_directive_str = [f"@{str(i)}" for i in _duplicate_default_directives]
        raise DirectiveValidationError(
            f"{formatted_directive_str} are reserved directives for client queries."
        )

    return Schema(
        query=query,
        mutation=mutation,
        subscription=subscription,
        types=types,
        directives=directives,
        auto_camelcase=auto_camelcase,
        include_graphql_spec_directives=include_graphql_spec_directives,
        schema_directives=schema_directives,
    )
