import re
from typing import Union

from graphql import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLInterfaceType,
    GraphQLObjectType,
)
from graphql.utilities.print_schema import (
    print_description,
    print_enum,
    print_fields,
    print_input_object,
)


def _remove_block(str_fields: str) -> str:
    # Remove blocks added by `print_block`
    block_match = re.match(
        r" \{\n(?P<field_str>.*)\n}",
        str_fields,
        flags=re.DOTALL,  # noqa
    )
    if block_match:
        str_fields = block_match.groups()[0]
    return str_fields


def entity_type_to_fields_string(
    field: Union[GraphQLObjectType, GraphQLInterfaceType],
) -> str:
    return _remove_block(print_fields(field))


def enum_type_to_fields_string(graphene_type: GraphQLEnumType) -> str:
    fields = print_enum(graphene_type).replace(
        print_description(graphene_type) + f"enum {graphene_type.name}", ""
    )
    return _remove_block(fields)


def input_type_to_fields_string(graphene_type: GraphQLInputObjectType) -> str:
    fields = print_input_object(graphene_type).replace(
        print_description(graphene_type) + f"input {graphene_type.name}", ""
    )
    return _remove_block(fields)
