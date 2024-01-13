from pathlib import Path

import pytest
from graphql import (
    DirectiveLocation as GrapheneDirectiveLocation,
    GraphQLArgument,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_directives import CustomDirective, DirectiveLocation
from graphene_directives.exceptions import DirectiveInvalidArgTypeError

curr_dir = Path(__file__).parent


def test_invalid_location_types() -> None:
    with pytest.raises(Exception) as e_info:
        CustomDirective(
            name="cache",
            locations=[GrapheneDirectiveLocation.FIELD, DirectiveLocation.OBJECT],
            args={
                "max_age": GraphQLArgument(
                    GraphQLNonNull(GraphQLInt),
                    description="Specifies the maximum age for cache in seconds.",
                ),
                "swr": GraphQLArgument(
                    GraphQLInt,
                    description="Stale-while-revalidate value in seconds. Optional.",
                ),
                "scope": GraphQLArgument(
                    GraphQLString, description="Scope of the cache. Optional."
                ),
            },
            description="Caching directive to control cache behavior of fields or fragments.",
        )

    assert e_info.type == DirectiveInvalidArgTypeError


def test_invalid_location_types_allow() -> None:
    CustomDirective(
        name="cache",
        locations=[GrapheneDirectiveLocation.FIELD, DirectiveLocation.OBJECT],
        args={
            "max_age": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Specifies the maximum age for cache in seconds.",
            ),
            "swr": GraphQLArgument(
                GraphQLInt,
                description="Stale-while-revalidate value in seconds. Optional.",
            ),
            "scope": GraphQLArgument(
                GraphQLString, description="Scope of the cache. Optional."
            ),
        },
        description="Caching directive to control cache behavior of fields or fragments.",
        allow_all_directive_locations=True,
    )


def test_correct_location() -> None:
    CustomDirective(
        name="cache",
        locations=list(DirectiveLocation),
        args={
            "max_age": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Specifies the maximum age for cache in seconds.",
            ),
            "swr": GraphQLArgument(
                GraphQLInt,
                description="Stale-while-revalidate value in seconds. Optional.",
            ),
            "scope": GraphQLArgument(
                GraphQLString, description="Scope of the cache. Optional."
            ),
        },
        description="Caching directive to control cache behavior of fields or fragments.",
        allow_all_directive_locations=False,
    )

    CustomDirective(
        name="cache2",
        locations=list(GrapheneDirectiveLocation),
        args={
            "max_age": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Specifies the maximum age for cache in seconds.",
            ),
            "swr": GraphQLArgument(
                GraphQLInt,
                description="Stale-while-revalidate value in seconds. Optional.",
            ),
            "scope": GraphQLArgument(
                GraphQLString, description="Scope of the cache. Optional."
            ),
        },
        description="Caching directive to control cache behavior of fields or fragments.",
        allow_all_directive_locations=True,
    )
