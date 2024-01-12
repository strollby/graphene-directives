from dataclasses import dataclass
from typing import Any

from graphql import DirectiveLocation as GrapheneDirectiveLocation
from graphql import GraphQLDirective

from ..exceptions import DirectiveValidationError


@dataclass
class SchemaDirective:
    target_directive: GraphQLDirective
    arguments: dict[str, Any]

    def __post_init__(self):
        if GrapheneDirectiveLocation.SCHEMA not in self.target_directive.locations:
            raise DirectiveValidationError(
                ". ".join(
                    [
                        f"{self.target_directive} cannot be used as schema directive",
                        "Missing DirectiveLocation.SCHEMA in locations",
                    ]
                )
            )
