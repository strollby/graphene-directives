from pathlib import Path

import graphene
import pytest
from graphql import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_directives import (
    CustomDirective,
    DirectiveLocation,
    directive,
    build_schema,
)
from graphene_directives.exceptions import DirectiveInvalidArgValueTypeError

curr_dir = Path(__file__).parent

CacheDirective = CustomDirective(
    name="cache",
    locations=[DirectiveLocation.OBJECT, DirectiveLocation.FIELD_DEFINITION],
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
    is_repeatable=True,
)

DbCacheDirective = CustomDirective(
    name="db_cache",
    locations=[DirectiveLocation.OBJECT, DirectiveLocation.FIELD_DEFINITION],
    args={
        "max_age": GraphQLArgument(
            GraphQLNonNull(GraphQLInt),
            description="Specifies the maximum age for cache in seconds.",
            default_value=12,
        ),
        "swr": GraphQLArgument(
            GraphQLInt, description="Stale-while-revalidate value in seconds. Optional."
        ),
        "scope": GraphQLArgument(
            GraphQLString, description="Scope of the cache. Optional."
        ),
    },
    description="Caching directive to control cache behavior of fields or fragments.",
)

AuthenticatedDirective = CustomDirective(
    name="authenticated",
    locations=[DirectiveLocation.ARGUMENT_DEFINITION],
    args={
        "required": GraphQLArgument(
            GraphQLNonNull(GraphQLBoolean), description="Auth required"
        )
    },
    description="Auth directive to control authorization behavior.",
)

RequiresDirective = CustomDirective(
    name="requires",
    locations=[DirectiveLocation.FIELD_DEFINITION],
    args={
        "fields": GraphQLArgument(
            GraphQLNonNull(GraphQLString),
            description="Fields required from other services.",
        )
    },
    description="Requires directive to pull in fields from other services.",
)


def test_input_argument_on_class() -> None:
    with pytest.raises(Exception) as e_info:

        @directive(target_directive=CacheDirective, required=True)
        class _TestClass(graphene.ObjectType):
            age = graphene.Int(required=True)

    assert e_info.type == DirectiveInvalidArgValueTypeError


def test_input_argument_on_field() -> None:
    with pytest.raises(Exception) as e_info:

        class _TestClass(graphene.ObjectType):
            age = graphene.Int(required=True)
            kind = directive(
                target_directive=CacheDirective,
                field=graphene.Int(
                    required=True,
                    deprecation_reason="This field is deprecated and will be removed in future",
                ),
            )

    assert e_info.type == DirectiveInvalidArgValueTypeError


def test_input_default_argument_on_class() -> None:
    @directive(target_directive=DbCacheDirective, required=True)
    class _TestClass(graphene.ObjectType):
        age = graphene.Int(required=True)


def test_input_default_argument_on_field() -> None:
    class _TestClass(graphene.ObjectType):
        age = graphene.Int(required=True)
        kind = directive(
            target_directive=DbCacheDirective,
            field=graphene.Int(
                required=True,
                deprecation_reason="This field is deprecated and will be removed in future",
            ),
        )


def test_field_argument_camel_casing() -> None:
    """Test that argument names are converted to camel-case."""

    class Position(graphene.ObjectType):
        x = graphene.Int(required=True)
        y = graphene.Int(required=True)

    class Query(graphene.ObjectType):
        # A decorated field with a directive that has an argument
        position = directive(
            CacheDirective,
            field=graphene.Field(Position, some_arg=graphene.Int(required=True)),
            max_age=300,
        )

        # A non-decorated field without directive that has an argument
        field = graphene.Field(
            graphene.Int,
            some_arg=graphene.Int(required=True),
            some_other_arg=graphene.Int(required=True),
            description="A field",
        )

        # A non-decorated field with a name that gets camelCased without directive that has an argument
        some_other_field = graphene.Field(
            graphene.String,
            some_arg=graphene.Int(required=True),
            description="An other field",
        )

    schema_with_directive = build_schema(query=Query, directives=(CacheDirective,))

    with open(
        f"{curr_dir}/schema_files/test_directive_arguments_camel_case.graphql"
    ) as f:
        schema = str(schema_with_directive)

        assert schema == f.read()


def test_argument_directive_survives_multiple_directives_on_field() -> None:
    """Argument directives were silently dropped for multi-word field names
    (e.g. `banana_split` -> `bananaSplit`) when also wrapped in a
    field-level directive."""

    class Meta(graphene.ObjectType):
        x = graphene.String()

    class Query(graphene.ObjectType):
        banana_split = directive(
            RequiresDirective,
            field=graphene.Field(
                Meta,
                access_token=directive(
                    AuthenticatedDirective,
                    field=graphene.Argument(graphene.String),
                    required=True,
                ),
                description="desc",
            ),
            fields="id",
        )

    schema = build_schema(
        query=Query, directives=(AuthenticatedDirective, RequiresDirective)
    )

    with open(
        f"{curr_dir}/schema_files/test_directive_arguments_multiple_applied.graphql"
    ) as f:
        assert str(schema) == f.read()
