from pathlib import Path

import graphene
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull, GraphQLString

from graphene_directives import (
    CustomDirective,
    DirectiveLocation,
    build_schema,
    directive_decorator,
)

curr_dir = Path(__file__).parent

CacheDirective = CustomDirective(
    name="cache",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.OBJECT,
        DirectiveLocation.UNION,
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
)


cache = directive_decorator(target_directive=CacheDirective)


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


schema = build_schema(query=Query, types=(SearchResult,), directives=[CacheDirective])


def test_generate_schema() -> None:
    with open(f"{curr_dir}/schema_files/test_directive_using_helper.graphql") as f:
        assert str(schema) == f.read()
