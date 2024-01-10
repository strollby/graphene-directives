from copy import deepcopy
from typing import Any
from typing import Union

from graphql import (
    GraphQLDirective,
    GraphQLEnumType,
    GraphQLField,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLObjectType,
)


def get_single_field_type(
    entity: Union[GraphQLEnumType, GraphQLInputObjectType, GraphQLObjectType],
    field_name: str,
    field_type: Union[GraphQLInputField, GraphQLField],
    is_enum_type: bool = False,
) -> Union[GraphQLEnumType, GraphQLInputObjectType, GraphQLObjectType]:
    """
    Generates the schema for a type with just one given field
    """
    new_entity = deepcopy(entity)
    setattr(
        new_entity, "values" if is_enum_type else "fields", {field_name: field_type}
    )
    return new_entity


def field_attribute_name(target_directive: GraphQLDirective) -> str:
    return f"_directive_{target_directive.name}_field"


def non_field_attribute_name(target_directive: GraphQLDirective) -> str:
    return f"_directive_{target_directive.name}_non_field"


def has_field_attribute(type_: Any, target_directive: GraphQLDirective) -> bool:  # noqa: ANN401
    return hasattr(type_, field_attribute_name(target_directive))


def has_non_field_attribute(type_: Any, target_directive: GraphQLDirective) -> bool:  # noqa: ANN401
    return hasattr(type_, non_field_attribute_name(target_directive))


def get_field_attribute_value(type_: Any, target_directive: GraphQLDirective) -> dict:  # noqa: ANN401
    return getattr(type_, field_attribute_name(target_directive))


def get_non_field_attribute_value(
    type_: Any,  # noqa: ANN401
    target_directive: GraphQLDirective,
) -> dict:
    return getattr(type_, non_field_attribute_name(target_directive))
