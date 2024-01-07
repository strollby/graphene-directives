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

from graphene_directives import build_decorator_from_directive, build_schema

curr_dir = os.path.dirname(os.path.realpath(__file__))

CacheDirective = GraphQLDirective(
    name="cache",
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


cache = build_decorator_from_directive(target_directive=CacheDirective)


@cache(max_age=100)
class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = cache(field=graphene.Int(required=True), max_age=60)


@cache(max_age=60)
class Human(graphene.ObjectType):
    name = graphene.String()
    born_in = graphene.String()


@cache(max_age=200)
class Droid(graphene.ObjectType):
    name = cache(field=graphene.String(), max_age=300)
    primary_function = graphene.String()


@cache(max_age=200)
class Starship(graphene.ObjectType):
    name = graphene.String()
    length = cache(field=graphene.Int(deprecation_reason="Koo"), max_age=60)


@cache(max_age=500)
class SearchResult(graphene.Union):
    class Meta:
        types = (Human, Droid, Starship)


class Query(graphene.ObjectType):
    position = graphene.Field(Position, deprecation_reason="Koo")


schema = build_schema(query=Query, types=(SearchResult,), directives=[CacheDirective])  # noqa


def test_cache() -> None:
    with open(f"{curr_dir}/schema_files/test_cache.graphql") as f:
        assert str(schema) == f.read()
