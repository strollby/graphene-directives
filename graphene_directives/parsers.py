import json
import re
from typing import Any, Collection, Dict, Union, cast

from graphene.utils.str_converters import to_camel_case, to_snake_case
from graphql import (
    GraphQLDirective,
    GraphQLEnumType,
    GraphQLError,
    GraphQLInputObjectType,
    GraphQLInputType,
    GraphQLInterfaceType,
    GraphQLObjectType,
    is_non_null_type,
    value_from_ast,
)
from graphql.pyutils import inspect, print_path_list
from graphql.utilities import coerce_input_value
from graphql.utilities.print_schema import (
    print_description,
    print_enum,
    print_fields,
    print_input_object,
)

from .data_models import SchemaDirective
from .exceptions import DirectiveInvalidArgValueTypeError


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
            + (f'"{value}"' if isinstance(value, str) else json.dumps(value))
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
        args = parse_argument_values(
            schema_directive.target_directive,
            {
                to_camel_case(field): value
                for (field, value) in schema_directive.arguments.items()
            },
        )
        schema_directives_strings.append(
            "\t" + decorator_string(schema_directive.target_directive, **args)
        )

    if len(schema_directives_strings) != 0:
        string_schema += (
            "extend schema\n" + "\n".join(schema_directives_strings) + "\n\n"
        )

    return string_schema


def parse_argument_values(
    directive: GraphQLDirective, inputs: Dict[str, Any]
) -> dict[str, Any]:
    coerced_values: Dict[str, Any] = {}
    errors = []

    for var_name, var_arg_type in directive.args.items():
        var_type = var_arg_type.type
        snake_cased_var_name = to_snake_case(var_name)

        var_type = cast(GraphQLInputType, var_type)
        if var_name not in inputs:
            if var_arg_type.default_value:
                coerced_values[var_name] = value_from_ast(
                    var_arg_type.default_value, var_type
                )
            elif is_non_null_type(var_type):
                var_type_str = inspect(var_type)
                errors.append(
                    f"Variable '{snake_cased_var_name}' of required type '{var_type_str}'"
                    " was not provided."
                )
            continue

        value = inputs[var_name]
        if value is None and is_non_null_type(var_type):
            var_type_str = inspect(var_type)
            errors.append(
                f"Variable '{snake_cased_var_name}' of non-null type '{var_type_str}'"
                " must not be null."
            )
            continue

        def on_input_value_error(
            path: list[Union[str, int]], invalid_value: Any, error: GraphQLError
        ) -> None:
            invalid_str = inspect(invalid_value)
            prefix = (
                f"Variable '{snake_cased_var_name}' got invalid value {invalid_str}"
            )
            if path:
                prefix += f" at '{snake_cased_var_name}{print_path_list(path)}'"
            errors.append(prefix + "; " + error.message)

        coerced_values[var_name] = coerce_input_value(
            value, var_type, on_input_value_error
        )

    if errors:
        raise DirectiveInvalidArgValueTypeError(errors=errors)

    return coerced_values


def arg_camel_case(inputs: dict) -> dict:
    return {to_camel_case(k): v for k, v in inputs.items()}


def arg_snake_case(inputs: dict) -> dict:
    return {to_snake_case(k): v for k, v in inputs.items()}
