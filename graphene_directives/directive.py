from functools import partial
from typing import Any, Callable, Collection, Dict, Optional

from graphene.utils.str_converters import to_camel_case
from graphql import GraphQLArgument, GraphQLDirective
from graphql.language import ast

from .constants import ACCEPTED_TYPES, FIELD_TYPES, LOCATION_NON_FIELD_VALIDATOR
from .constants import DirectiveLocation
from .data_models import CustomDirectiveMeta
from .exceptions import (
    DirectiveInvalidArgTypeError,
    DirectiveInvalidTypeError,
    DirectiveValidationError,
)
from .parsers import parse_argument_values
from .utils import field_attribute_name, non_field_attribute_name, set_attribute_value


def CustomDirective(  # noqa
    name: str,
    locations: Collection[DirectiveLocation],
    args: Optional[Dict[str, GraphQLArgument]] = None,
    is_repeatable: bool = False,
    description: Optional[str] = None,
    extensions: Optional[Dict[str, Any]] = None,
    ast_node: Optional[ast.DirectiveDefinitionNode] = None,
    allow_all_directive_locations: bool = False,
    add_definition_to_schema: bool = True,
    non_field_validator: Callable[[Any, dict[str, Any], Any], bool] = None,
    field_validator: Callable[[Any, Any, dict[str, Any], Any], bool] = None,
    input_transform: Callable[[dict[str, Any], Any], dict[str, Any]] = None,
) -> GraphQLDirective:
    """
    Creates a GraphQLDirective

    :param name: (GraphQLDirective param)
    :param args: (GraphQLDirective param)
    :param is_repeatable: (GraphQLDirective param)
    :param description: (GraphQLDirective param)
    :param extensions: (GraphQLDirective param)
    :param ast_node: (GraphQLDirective param)

    :param locations: list[DirectiveLocation], if need to use unsupported locations, set allow_all_directive_locations True
    :param allow_all_directive_locations: Allow other DirectiveLocation other than the ones supported by library
    :param add_definition_to_schema: If false, the @directive definition is not added to the graphql schema
    :param non_field_validator: a non field validator function
                def validator (type_: graphene type, inputs: Any, schema: Schema) -> bool,
                    if validator returns False, library raises DirectiveCustomValidationError
    :param field_validator: a field validator function
                def validator (parent_type_: graphene_type, field_type_: graphene type, inputs: Any, schema: Schema) -> bool,
                    if validator returns False, library raises DirectiveCustomValidationError

    :param input_transform: a function to transform the input arg's values before usage
                def input_transform (inputs: dict[str, Any], schema: Schema) -> dict[str, Any]

    """

    if not isinstance(allow_all_directive_locations, bool):
        raise DirectiveInvalidArgTypeError(
            f"directive @{name} allow_all_directive_locations type invalid expected bool"
        )

    if not isinstance(add_definition_to_schema, bool):
        raise DirectiveInvalidArgTypeError(
            f"directive @{name} add_definition_to_schema type invalid expected bool"
        )

    if not (isinstance(non_field_validator, Callable) or non_field_validator is None):
        raise DirectiveInvalidArgTypeError(
            f"directive @{name} validator type invalid expected Callable[[GraphQLDirective, Any], bool] "
        )

    if (
        any(not isinstance(location, DirectiveLocation) for location in locations)
        and not allow_all_directive_locations
    ):
        raise DirectiveInvalidArgTypeError(
            f"directive @{name} location type invalid expected {DirectiveLocation} from graphene_directives"
        )

    if args is not None:
        camel_cased_args = {}
        for arg_name, arg_value in args.items():
            camel_cased_args[to_camel_case(arg_name)] = arg_value
    else:
        camel_cased_args = args

    target_directive = GraphQLDirective(
        name=name,
        locations=[
            location.to_graphene_directive_location()
            if isinstance(location, DirectiveLocation)
            else location
            for location in locations
        ],
        args=camel_cased_args,
        is_repeatable=is_repeatable,
        description=description,
        extensions=extensions,
        ast_node=ast_node,
    )

    valid_types = set(target_directive.locations).intersection(ACCEPTED_TYPES)
    non_field_types = set(valid_types).difference(FIELD_TYPES)
    supports_field_types = FIELD_TYPES.intersection(valid_types) != 0
    supports_non_field_types = (
        set(LOCATION_NON_FIELD_VALIDATOR.values()).intersection(valid_types) != 0
    )

    target_directive._graphene_directive = CustomDirectiveMeta(
        allow_all_directive_locations=allow_all_directive_locations,
        add_definition_to_schema=add_definition_to_schema,
        has_no_argument=target_directive.args == {},
        valid_types=valid_types,
        non_field_types=non_field_types,
        supports_field_types=supports_field_types,
        supports_non_field_types=supports_non_field_types,
        non_field_validator=non_field_validator,
        field_validator=field_validator,
        input_transform=input_transform,
    )

    # Check if target_directive.locations have accepted types
    if (
        len(valid_types) != len(target_directive.locations)
        and not allow_all_directive_locations
    ):
        invalid_types = [
            str(i) for i in set(target_directive.locations).difference(ACCEPTED_TYPES)
        ]
        raise DirectiveValidationError(
            ", ".join(
                [
                    f"{str(target_directive)}: Directives don't support types: {invalid_types}",
                    f"allowed types: {[str(i) for i in ACCEPTED_TYPES]}",
                ]
            )
        )

    return target_directive


def directive(
    target_directive: GraphQLDirective, *, field: Optional[Any] = None, **_kwargs: Any
) -> Callable:
    """
    Decorator to use to add directive a given type of field.
    """

    if not hasattr(target_directive, "_graphene_directive"):
        raise DirectiveInvalidTypeError(target_directive)

    meta_data: CustomDirectiveMeta = getattr(target_directive, "_graphene_directive")

    # Converting inputs to camel_case

    kwargs = {to_camel_case(field): value for (field, value) in _kwargs.items()}
    directive_name = str(target_directive)

    kwargs = parse_argument_values(target_directive, kwargs)

    def decorator(type_: Any) -> Any:
        if not meta_data.supports_non_field_types:
            raise DirectiveValidationError(
                f"{directive_name} cannot be used at non field level"
            )

        if not any(
            LOCATION_NON_FIELD_VALIDATOR[valid_type](type_)
            for valid_type in meta_data.non_field_types
        ):
            raise DirectiveValidationError(
                f"{directive_name} cannot be used for {type_}, valid levels are: {[str(i) for i in meta_data.valid_types]}"
            )

        set_attribute_value(
            type_=type_,
            attribute_name=non_field_attribute_name(target_directive),
            target_directive=target_directive,
            data={} if meta_data.has_no_argument else kwargs,
        )
        return type_

    if field:
        if not meta_data.supports_field_types:
            raise DirectiveValidationError(
                f"{directive_name} cannot be used at field level"
            )

        set_attribute_value(
            type_=field,
            attribute_name=field_attribute_name(target_directive),
            target_directive=target_directive,
            data={} if meta_data.has_no_argument else kwargs,
        )

        return field

    return decorator


def directive_decorator(target_directive: GraphQLDirective) -> directive:
    """
    Build a decorator for given target directive
    :param target_directive: GraphQLDirective

    Returns partial of directive(target_directive=target_directive)
    """

    return partial(directive, target_directive=target_directive)
