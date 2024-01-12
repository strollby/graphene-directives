from dataclasses import dataclass
from typing import Any, Callable, Union

from graphql import DirectiveLocation as GrapheneDirectiveLocation, GraphQLDirective


@dataclass
class CustomDirectiveMeta:
    allow_all_directive_locations: bool
    add_definition_to_schema: bool
    has_no_argument: bool
    valid_types: set[GrapheneDirectiveLocation]
    non_field_types: set[GrapheneDirectiveLocation]
    supports_field_types: bool
    supports_non_field_types: bool
    validator: Union[Callable[[GraphQLDirective, Any], bool], None]
