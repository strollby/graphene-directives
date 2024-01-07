from functools import partial

from graphql import GraphQLDirective

from graphene_directives import directive


def build_decorator_from_directive(target_directive: GraphQLDirective) -> directive:
    """
    Build a decorator for given target directive

    Returns partial of directive(target_directive=target_directive)
    """
    return partial(directive, target_directive=target_directive)
