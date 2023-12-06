import graphene
from graphql import (
    GraphQLDirective,
    DirectiveLocation,
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLInt,
    GraphQLString,
)

from graphene_directives import build_schema, directive

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
    assert str(schema).strip("\n") == (
        '"""Caching directive to control cache behavior of fields or fragments."""\n'
        "directive @stellate_cache(\n"
        ' """Specifies the maximum age for cache in seconds."""\n'
        " maxAge: Int!\n"
        "\n"
        ' """Stale-while-revalidate value in seconds. Optional."""\n'
        " swr: Int\n"
        "\n"
        ' """Scope of the cache. Optional."""\n'
        " scope: String\n"
        ") on FIELD | OBJECT\n"
        "\n"
        "union SearchResult @stellate_cache(maxAge: 500) = Human | Droid | Starship\n"
        "\n"
        "type Human @stellate_cache(maxAge: 60) {\n"
        " name: String\n"
        " bornIn: String\n"
        "}\n"
        "\n"
        "type Droid @stellate_cache(maxAge: 200) {\n"
        " name: String @stellate_cache(maxAge: 300)\n"
        " primaryFunction: String\n"
        "}\n"
        "\n"
        "type Starship @stellate_cache(maxAge: 200) {\n"
        " name: String\n"
        ' length: Int @deprecated(reason: "Koo") @stellate_cache(maxAge: 60)\n'
        "}\n"
        "\n"
        "type Query {\n"
        ' position: Position @deprecated(reason: "Koo")\n'
        "}\n"
        "\n"
        "type Position @stellate_cache(maxAge: 100) {\n"
        " x: Int!\n"
        " y: Int! @stellate_cache(maxAge: 60)\n"
        "}"
    )
