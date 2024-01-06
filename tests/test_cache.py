import os

import graphene
from graphql import (
    DirectiveLocation,
    GraphQLArgument,
    GraphQLDirective,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_directives import build_schema, directive

curr_dir = os.path.dirname(os.path.realpath(__file__))

StellateCacheDirective = GraphQLDirective(
    name="stellate_cache",
    locations=[DirectiveLocation.FIELD, DirectiveLocation.OBJECT],
    args={
        "maxAge": GraphQLArgument(
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
)


@directive(target_directive=StellateCacheDirective, max_age=100)
class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = directive(
        target_directive=StellateCacheDirective,
        field=graphene.Int(required=True),
        max_age=60,
    )


@directive(target_directive=StellateCacheDirective, max_age=60)
class Human(graphene.ObjectType):
    name = graphene.String()
    born_in = graphene.String()


@directive(StellateCacheDirective, max_age=200)
class Droid(graphene.ObjectType):
    name = directive(StellateCacheDirective, field=graphene.String(), max_age=300)
    primary_function = graphene.String()


@directive(StellateCacheDirective, max_age=200)
class Starship(graphene.ObjectType):
    name = graphene.String()
    length = directive(
        target_directive=StellateCacheDirective,
        field=graphene.Int(deprecation_reason="Koo"),
        max_age=60,
    )


@directive(target_directive=StellateCacheDirective, max_age=500)
class SearchResult(graphene.Union):
    class Meta:
        types = (Human, Droid, Starship)


class Query(graphene.ObjectType):
    position = graphene.Field(Position, deprecation_reason="Koo")


schema = build_schema(
    query=Query, types=(SearchResult,), directives=[StellateCacheDirective]
)  # noqa


def test_cache() -> None:
    with open(f"{curr_dir}/schema_files/test_cache.graphql") as f:
        assert str(schema) == f.read()
