from typing import Any, Callable

import graphene


def directive(
    name: str,
    field: Any | None = None,  # noqa
    **kwargs: Any,  # noqa
) -> Callable:
    """
    Decorator to use to add directive a given type of field.
    """

    # noinspection PyProtectedMember,PyPep8Naming
    def decorator(type_: graphene.ObjectType) -> graphene.ObjectType:
        setattr(type_, f"_{name}", kwargs)
        return type_

    if field:
        setattr(field, f"_{name}", kwargs)
        return field
    return decorator
