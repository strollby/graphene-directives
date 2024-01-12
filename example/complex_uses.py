import os
from typing import Any

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
    SchemaDirective,
    build_schema,
    directive,
)

curr_dir = os.path.dirname(os.path.realpath(__file__))


def validate_non_field_input(_type: Any, inputs: dict) -> bool:
    """
    def validator (type_: graphene type, inputs: Any) -> bool,
    if validator returns False, library raises DirectiveCustomValidationError
    """
    if inputs.get("max_age") > 2500:
        return False
    return True


def validate_field_input(_parent_type: Any, _field_type: Any, inputs: dict) -> bool:
    """
    def validator (parent_type_: graphene_type, field_type_: graphene type, inputs: Any) -> bool,
    if validator returns False, library raises DirectiveCustomValidationError
    """
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
    non_field_validator=validate_non_field_input,
    field_validator=validate_field_input,
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
        DirectiveLocation.SCALAR,
        DirectiveLocation.ARGUMENT_DEFINITION,
    ],
    args={
        "required": GraphQLArgument(
            GraphQLNonNull(GraphQLBoolean), description="Auth required"
        )
    },
    description="Auth directive to control authorization behavior.",
)

# This will prevent @key definition from being added to the schema, but decorator will work
KeyDirective = CustomDirective(
    name="key",
    locations=[DirectiveLocation.OBJECT, DirectiveLocation.INTERFACE],
    description="Declaring an entity",
    add_definition_to_schema=False,
)

# No argument directive
InternalDirective = CustomDirective(
    name="internal",
    locations=[
        DirectiveLocation.OBJECT,
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.ARGUMENT_DEFINITION,
    ],
    description="Directive to indicate this is a internal field.",
)

# A Repeatable directive
RepeatableDirective = CustomDirective(
    name="repeatable_directive",
    locations=[DirectiveLocation.OBJECT, DirectiveLocation.FIELD_DEFINITION],
    description="A repeatable directive.",
    args={
        "service_name": GraphQLArgument(
            GraphQLNonNull(GraphQLString), description="Service Name required"
        )
    },
    is_repeatable=True,
)

# A Schema directive
ComposeDirective = CustomDirective(
    name="compose",
    locations=[DirectiveLocation.SCHEMA],
    description="A schema directive.",
    args={
        "directive_name": GraphQLArgument(
            GraphQLNonNull(GraphQLString), description="Directive Name required"
        )
    },
    is_repeatable=True,
)


@directive(target_directive=CacheDirective, max_age=100)
@directive(target_directive=AuthenticatedDirective, required=True)
class Animal(graphene.Interface):  # DirectiveLocation.INTERFACE
    age = graphene.Int(required=True)
    kind = directive(
        target_directive=CacheDirective, field=graphene.Int(required=True), max_age=60
    )  # DirectiveLocation.FIELD_DEFINITION


@directive(target_directive=CacheDirective, max_age=100)
@directive(target_directive=AuthenticatedDirective, required=True)
class TruthEnum(graphene.Enum):  # DirectiveLocation.ENUM
    A = 1
    B = 2


# Add directives to enum values [DirectiveLocation.ENUM_VALUE]
directive(field=TruthEnum.A, target_directive=AuthenticatedDirective, required=True)


@directive(target_directive=CacheDirective, max_age=100)
class Position(graphene.ObjectType):  # DirectiveLocation.OBJECT
    x = graphene.Int(required=True)
    y = directive(
        target_directive=CacheDirective, field=graphene.Int(required=True), max_age=60
    )


@directive(target_directive=CacheDirective, max_age=60)  # DirectiveLocation.OBJECT
class Human(graphene.ObjectType):
    name = graphene.String()
    born_in = graphene.String()


@directive(target_directive=CacheDirective, max_age=60)
@directive(target_directive=AuthenticatedDirective, required=True)
class HumanInput(graphene.InputObjectType):  # DirectiveLocation.INPUT_OBJECT
    born_in = graphene.String()
    name = directive(  # DirectiveLocation.INPUT_FIELD_DEFINITION
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


@directive(CacheDirective, max_age=200)
class Starship(graphene.ObjectType):
    name = graphene.String()
    length = directive(
        target_directive=CacheDirective,
        field=graphene.Int(deprecation_reason="Use another field"),
        max_age=60,
    )


@directive(target_directive=CacheDirective, max_age=500)
@directive(target_directive=AuthenticatedDirective, required=True)
class SearchResult(graphene.Union):  # DirectiveLocation.UNION
    class Meta:
        types = (Human, Droid, Starship)


@directive(target_directive=CacheDirective, max_age=500)
@directive(target_directive=AuthenticatedDirective, required=True)
class DateNewScalar(graphene.Scalar):  # DirectiveLocation.SCALAR
    pass


@directive(target_directive=KeyDirective)
@directive(target_directive=InternalDirective)
class Admin(graphene.ObjectType):
    name = graphene.String()
    password = graphene.String()


@directive(target_directive=AuthenticatedDirective, required=True)
class User(graphene.ObjectType):
    name = graphene.String()
    password = graphene.String()
    price = graphene.Field(
        graphene.String,
        currency=directive(  # DirectiveLocation.ARGUMENT_DEFINITION
            InternalDirective, field=graphene.Argument(graphene.Int)
        ),  # Argument
        country=directive(  # Multiple DirectiveLocation.ARGUMENT_DEFINITION
            target_directive=AuthenticatedDirective,
            field=directive(InternalDirective, field=graphene.Argument(graphene.Int)),
            required=True,
        ),
    )


@directive(target_directive=RepeatableDirective, service_name="ProductService")
@directive(target_directive=RepeatableDirective, service_name="CompanyService")
@directive(target_directive=AuthenticatedDirective, required=True)
class Company(graphene.ObjectType):
    established = graphene.Int(required=True)
    name = directive(
        target_directive=RepeatableDirective,
        field=directive(
            target_directive=RepeatableDirective,
            field=graphene.String(
                required=True,
                deprecation_reason="This field is deprecated and will be removed in future",
            ),
            service_name="CompanyService Field",
        ),
        service_name="ProductService Field",
    )


class Query(graphene.ObjectType):
    position = graphene.Field(Position, deprecation_reason="unused field")


schema = build_schema(
    query=Query,
    types=(
        SearchResult,
        Animal,
        Admin,
        HumanInput,
        TruthEnum,
        DateNewScalar,
        User,
        Company,
    ),
    directives=(
        CacheDirective,
        AuthenticatedDirective,
        InternalDirective,
        KeyDirective,
        RepeatableDirective,
    ),
    schema_directives=(  # extend schema directives
        SchemaDirective(
            target_directive=ComposeDirective, arguments={"directive_name": "lowercase"}
        ),
        SchemaDirective(
            target_directive=ComposeDirective, arguments={"directive_name": "uppercase"}
        ),
        SchemaDirective(
            target_directive=ComposeDirective,
            arguments={"directive_name": "pascalcase"},
        ),
    ),
)


def generate_schema() -> None:
    with open(f"{curr_dir}/complex_uses.graphql", "w") as f:
        f.write(str(schema))


if __name__ == "__main__":
    generate_schema()
