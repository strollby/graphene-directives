from pathlib import Path

import graphene
import pytest
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull, GraphQLString

from graphene_directives import (
    CustomDirective,
    DirectiveLocation,
    DirectiveValidationError,
    directive,
)

curr_dir = Path(__file__).parent

CacheDirective = CustomDirective(
    name="cache",
    locations=[DirectiveLocation.FIELD_DEFINITION, DirectiveLocation.OBJECT],
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


def test_duplicate_values() -> None:
    with pytest.raises(Exception) as e_info:

        @directive(CacheDirective, max_age=20)
        @directive(CacheDirective, max_age=20)
        class _Test(graphene.ObjectType):
            pass

    assert e_info.type == DirectiveValidationError


def test_non_duplicate_values() -> None:
    @directive(CacheDirective, max_age=20)
    @directive(CacheDirective, max_age=22)
    class _Test(graphene.ObjectType):
        pass
