import os

import graphene
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
    build_schema,
    directive,
)

curr_dir = os.path.dirname(os.path.realpath(__file__))

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

# No argument directive
HiddenDirective = CustomDirective(
    name="hidden",
    locations=[DirectiveLocation.OBJECT, DirectiveLocation.ARGUMENT_DEFINITION],
    description="Auth directive to control authorization behavior.",
    add_definition_to_schema=False,
)


@directive(target_directive=CacheDirective, max_age=100)
@directive(target_directive=AuthenticatedDirective, required=True)
class Animal(graphene.Interface):
    age = graphene.Int(required=True)
    kind = directive(
        target_directive=CacheDirective, field=graphene.Int(required=True), max_age=60
    )


@directive(target_directive=CacheDirective, max_age=100)
@directive(target_directive=AuthenticatedDirective, required=True)
class TruthEnum(graphene.Enum):
    A = 1
    B = 2


# Add directives to enum values
directive(field=TruthEnum.A, target_directive=AuthenticatedDirective, required=True)


@directive(target_directive=CacheDirective, max_age=100)
class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = directive(
        target_directive=CacheDirective, field=graphene.Int(required=True), max_age=60
    )


@directive(target_directive=CacheDirective, max_age=60)
class Human(graphene.ObjectType):
    name = graphene.String()
    born_in = graphene.String()


@directive(target_directive=CacheDirective, max_age=60)
@directive(target_directive=AuthenticatedDirective, required=True)
class HumanInput(graphene.InputObjectType):
    born_in = graphene.String()
    name = directive(
        CacheDirective,
        field=graphene.String(
            description="Test Description", deprecation_reason="Deprecated use born in"
        ),
        max_age=300,
    )


class Query(graphene.ObjectType):
    position = graphene.Field(Position, deprecation_reason="Koo")


schema = build_schema(
    query=Query,
    types=(Animal, TruthEnum, HumanInput, Human, Position),
    directives=(CacheDirective, AuthenticatedDirective, HiddenDirective),
)  # noqa


def test_generate_schema() -> None:
    with open(
        f"{curr_dir}/schema_files/test_arg_add_definition_to_schema.graphql"
    ) as f:
        assert str(schema) == f.read()
