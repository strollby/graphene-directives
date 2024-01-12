import re
from typing import Collection, Union

from graphene.utils.str_converters import to_camel_case
from graphql import (
    GraphQLDirective,
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

from .data_models import SchemaDirective


def _remove_block(str_fields: str) -> str:
    # Remove blocks added by `print_block`
    block_match = re.match(r" \{\n(?P<field_str>.*)\n}", str_fields, flags=re.DOTALL)
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


def decorator_string(directive: GraphQLDirective, **kwargs: dict) -> str:
    directive_name = str(directive)
    if len(directive.args) == 0:
        return directive_name

    # Format each keyword argument as a string, considering its type
    formatted_args = [
        (
            f"{to_camel_case(key)}: "
            + (f'"{value}"' if isinstance(value, str) else str(value))
        )
        for key, value in kwargs.items()
        if value is not None and to_camel_case(key) in directive.args
    ]

    # Construct the directive string
    return f"{directive_name}({', '.join(formatted_args)})"


def extend_schema_string(
    string_schema: str, schema_directives: Collection[SchemaDirective]
) -> str:
    schema_directives_strings = []
    for schema_directive in schema_directives:
        schema_directives_strings.append(
            "\t"
            + decorator_string(
                schema_directive.target_directive, **schema_directive.arguments
            )
        )

    if len(schema_directives_strings) != 0:
        string_schema += (
            "extend schema\n" + "\n".join(schema_directives_strings) + "\n\n"
        )

    return string_schema
