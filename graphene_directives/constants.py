from enum import Enum

import graphene
from graphql import DirectiveLocation as GrapheneDirectiveLocation

LOCATION_NON_FIELD_VALIDATOR = {
    GrapheneDirectiveLocation.SCHEMA: lambda t: issubclass(t, graphene.Schema),
    GrapheneDirectiveLocation.SCALAR: lambda t: issubclass(t, graphene.Scalar),
    GrapheneDirectiveLocation.OBJECT: lambda t: issubclass(t, graphene.ObjectType),
    GrapheneDirectiveLocation.INTERFACE: lambda t: issubclass(t, graphene.Interface),
    GrapheneDirectiveLocation.UNION: lambda t: issubclass(t, graphene.Union),
    GrapheneDirectiveLocation.ENUM: lambda t: issubclass(t, graphene.Enum),
    GrapheneDirectiveLocation.INPUT_OBJECT: lambda t: issubclass(
        t, graphene.InputObjectType
    ),
}


FIELD_TYPES = {
    GrapheneDirectiveLocation.FIELD_DEFINITION,
    GrapheneDirectiveLocation.INPUT_FIELD_DEFINITION,
    GrapheneDirectiveLocation.ENUM_VALUE,
    GrapheneDirectiveLocation.ARGUMENT_DEFINITION,
}

ACCEPTED_TYPES = FIELD_TYPES.union(set(LOCATION_NON_FIELD_VALIDATOR.keys()))

TYPE_STRING_MAPPING = {
    graphene.Scalar: "scalar",
    graphene.Union: "union",
    graphene.ObjectType: "type",
    graphene.Interface: "interface",
    graphene.Enum: "enum",
    graphene.InputObjectType: "input",
}


class DirectiveLocation(Enum):
    """The enum type representing the directive location values."""

    SCHEMA = "schema"
    SCALAR = "scalar"
    OBJECT = "object"
    FIELD_DEFINITION = "field definition"
    ARGUMENT_DEFINITION = "argument definition"
    INTERFACE = "interface"
    UNION = "union"
    ENUM = "enum"
    ENUM_VALUE = "enum value"
    INPUT_OBJECT = "input object"
    INPUT_FIELD_DEFINITION = "input field definition"

    def to_graphene_directive_location(self) -> GrapheneDirectiveLocation:
        return GrapheneDirectiveLocation(self.value)
