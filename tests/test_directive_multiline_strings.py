from pathlib import Path
from typing import Any

import graphene
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull, GraphQLString

from graphene_directives import (
    CustomDirective,
    DirectiveLocation,
    Schema,
    build_schema,
    directive,
)

curr_dir = Path(__file__).parent


def validate_non_field_input(_type: Any, inputs: dict, _schema: Schema) -> bool:
    """
    def validator (type_: graphene type, inputs: Any, schema: Schema) -> bool,
    if validator returns False, library raises DirectiveCustomValidationError
    """
    return not inputs.get("max_age") > 2500


def validate_field_input(
    _parent_type: Any, _field_type: Any, inputs: dict, _schema: Schema
) -> bool:
    """
    def validator (parent_type_: graphene_type, field_type_: graphene type, inputs: Any, schema: Schema) -> bool,
    if validator returns False, library raises DirectiveCustomValidationError
    """
    return not inputs.get("max_age") > 2500


CacheDirective = CustomDirective(
    name="cache",
    locations=[
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
        DirectiveLocation.ENUM,
        DirectiveLocation.UNION,
        DirectiveLocation.INPUT_OBJECT,
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.INPUT_FIELD_DEFINITION,
        DirectiveLocation.SCALAR,
    ],
    args={
        "max_age": GraphQLArgument(
            GraphQLNonNull(GraphQLInt),
            description="Specifies the maximum age for cache in seconds.",
        ),
        "swr": GraphQLArgument(
            GraphQLInt, description="Stale-while-revalidate value in seconds. Optional."
        ),
        "scope": GraphQLArgument(
            GraphQLString, description="Scope of the cache. Optional."
        ),
    },
    description="Caching directive to control cache behavior of fields or fragments.",
    non_field_validator=validate_non_field_input,
    field_validator=validate_field_input,
)


class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = graphene.Int(required=True)


class QueryNoDirective(graphene.ObjectType):
    position = graphene.Field(
        Position, deprecation_reason="Koo\n\nDeprecated on 2025-01-01"
    )


class QueryWithDirective(graphene.ObjectType):
    position = directive(
        CacheDirective,
        field=graphene.Field(
            Position, deprecation_reason="Koo\n\nDeprecated on 2025-01-01"
        ),
        max_age=300,
    )


schema_no_directive = build_schema(query=QueryNoDirective)

schema_with_directive = build_schema(
    query=QueryWithDirective, directives=(CacheDirective,)
)


def test_generate_schema_no_directive() -> None:
    with open(
        f"{curr_dir}/schema_files/test_directive_multiline_string_no_directive.graphql"
    ) as f:
        assert str(schema_no_directive) == f.read()


def test_generate_schema_with_directive() -> None:
    with open(
        f"{curr_dir}/schema_files/test_directive_multiline_string_with_directive.graphql"
    ) as f:
        assert str(schema_with_directive) == f.read()
