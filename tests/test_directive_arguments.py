from pathlib import Path

import graphene
import pytest
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull, GraphQLString

from graphene_directives import CustomDirective, DirectiveLocation, directive
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
