from typing import Any, Callable, Optional

import graphene
from graphql import GraphQLDirective


def directive(
    target_directive: GraphQLDirective,
    *,
    field: Optional[Any] = None,  # noqa
    **kwargs: Any,  # noqa
) -> Callable:
    """
    Decorator to use to add directive a given type of field.
    """

    def decorator(type_: graphene.ObjectType) -> graphene.ObjectType:
        setattr(type_, f"_{target_directive.name}", kwargs)
        return type_

    if field:
        setattr(field, f"_{target_directive.name}", kwargs)
        return field
    return decorator
