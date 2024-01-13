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
    DirectiveValidationError,
    build_schema,
    directive,
)

curr_dir = Path(__file__).parent


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
    is_repeatable=True,
)


AuthenticatedDirective = CustomDirective(
    name="authenticated",
    locations=[
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
        DirectiveLocation.ENUM,
        DirectiveLocation.ENUM_VALUE,
        DirectiveLocation.UNION,
        DirectiveLocation.INPUT_OBJECT,
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.ARGUMENT_DEFINITION,
        DirectiveLocation.SCALAR,
    ],
    args={
        "required": GraphQLArgument(
            GraphQLNonNull(GraphQLBoolean), description="Auth required"
        )
    },
    description="Auth directive to control authorization behavior.",
)


@directive(target_directive=CacheDirective, max_age=100)
@directive(target_directive=CacheDirective, max_age=30)
@directive(target_directive=AuthenticatedDirective, required=True)
class Animal(graphene.Interface):
    age = graphene.Int(required=True)
    kind = directive(
        target_directive=CacheDirective,
        field=directive(
            target_directive=CacheDirective,
            field=graphene.Int(
                required=True,
                deprecation_reason="This field is deprecated and will be removed in future",
            ),
            max_age=20,
        ),
        max_age=60,
    )


class Query(graphene.ObjectType):
    animals = graphene.Field(Animal, deprecation_reason="Koo")


schema = build_schema(query=Query, directives=(CacheDirective, AuthenticatedDirective))


def test_generate_schema() -> None:
    with open(f"{curr_dir}/schema_files/test_directive_with_repeatable.graphql") as f:
        assert str(schema) == f.read()


def test_non_repeatable_on_non_field() -> None:
    with pytest.raises(Exception) as e_info:

        @directive(target_directive=AuthenticatedDirective, required=True)
        @directive(target_directive=AuthenticatedDirective, required=True)
        class _TestClass(graphene.Interface):
            age = graphene.Int(required=True)
            kind = directive(
                target_directive=CacheDirective,
                field=directive(
                    target_directive=CacheDirective,
                    field=graphene.Int(
                        required=True,
                        deprecation_reason="This field is deprecated and will be removed in future",
                    ),
                    max_age=20,
                ),
                max_age=60,
            )

    assert e_info.type == DirectiveValidationError


def test_non_repeatable_on_field() -> None:
    with pytest.raises(Exception) as e_info:

        class _TestClass(graphene.Interface):
            age = graphene.Int(required=True)
            kind = directive(
                target_directive=AuthenticatedDirective,
                field=directive(
                    target_directive=AuthenticatedDirective,
                    field=graphene.Int(
                        required=True,
                        deprecation_reason="This field is deprecated and will be removed in future",
                    ),
                    required=True,
                ),
                required=False,
            )

    assert e_info.type == DirectiveValidationError
