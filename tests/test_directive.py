import os

import graphene
from graphql import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLDirective,
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


def validate_input(_directive: GraphQLDirective, inputs: dict) -> bool:
    if inputs.get("max_age") > 2500:
        return False
    return True


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
    validator=validate_input,
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
)


# No argument directive
LinkDirective = CustomDirective(
    name="link",
    locations=[DirectiveLocation.SCHEMA],
    description="Schema directive to link files",
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


@directive(CacheDirective, max_age=200)
class Droid(graphene.ObjectType):
    name = directive(
        CacheDirective,
        field=graphene.String(
            description="Test Description", deprecation_reason="Deprecated use born in"
        ),
        max_age=300,
    )
    primary_function = graphene.String()


@directive(CacheDirective, max_age=20)
class Starship(graphene.ObjectType):
    name = graphene.String()
    length = directive(
        target_directive=CacheDirective,
        field=graphene.Int(deprecation_reason="Koo"),
        max_age=60,
    )


@directive(target_directive=CacheDirective, max_age=500)
@directive(target_directive=AuthenticatedDirective, required=True)
class SearchResult(graphene.Union):
    class Meta:
        types = (Human, Droid, Starship)


@directive(target_directive=CacheDirective, max_age=500)
@directive(target_directive=AuthenticatedDirective, required=True)
class DateNewScalar(graphene.Scalar):
    pass


@directive(target_directive=AuthenticatedDirective, required=True)
class Admin(graphene.ObjectType):
    name = graphene.String()
    password = graphene.String()
    price = graphene.Field(
        graphene.String,
        currency=directive(
            HiddenDirective,
            field=graphene.Argument(graphene.Int, deprecation_reason="Use country"),
        ),  # Argument
        country=directive(
            target_directive=AuthenticatedDirective,
            field=directive(
                HiddenDirective,
                field=graphene.Argument(graphene.Int, description="Country"),
            ),
            required=True,
        ),  # Argument Definition (Multiple directives)
    )


@directive(target_directive=AuthenticatedDirective, required=True)
class User(graphene.ObjectType):
    name = graphene.String()
    password = graphene.String()
    price = graphene.Field(
        graphene.String,
        currency=directive(
            HiddenDirective, field=graphene.Argument(graphene.Int)
        ),  # Argument
        country=directive(
            target_directive=AuthenticatedDirective,
            field=directive(HiddenDirective, field=graphene.Argument(graphene.Int)),
            required=True,
        ),  # Argument Definition (Multiple directives)
    )


class Query(graphene.ObjectType):
    position = graphene.Field(Position, deprecation_reason="Koo")


schema = build_schema(
    query=Query,
    types=(SearchResult, Animal, Admin, HumanInput, TruthEnum, DateNewScalar, User),
    directives=(CacheDirective, AuthenticatedDirective, HiddenDirective, LinkDirective),
)  # noqa


def test_generate_schema() -> None:
    with open(f"{curr_dir}/schema_files/test_directive.graphql") as f:
        assert str(schema) == f.read()