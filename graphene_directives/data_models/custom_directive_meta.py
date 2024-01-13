from dataclasses import dataclass
from typing import Any, Callable, Union

from graphql import DirectiveLocation as GrapheneDirectiveLocation


@dataclass
class CustomDirectiveMeta:
    allow_all_directive_locations: bool
    add_definition_to_schema: bool
    has_no_argument: bool
    valid_types: set[GrapheneDirectiveLocation]
    non_field_types: set[GrapheneDirectiveLocation]
    supports_field_types: bool
    supports_non_field_types: bool
    input_transform: Union[
        Callable[[dict[str, Any], Any], dict[str, Any]], None
    ]  # (args, schema) -> args
    non_field_validator: Union[
        Callable[[Any, dict[str, Any], Any], bool], None
    ]  # (type, args, schema) -> valid
    field_validator: Union[
        Callable[[Any, Any, dict[str, Any], Any], bool], None
    ]  # (parent_type, field_type, args, schema) -> valid
