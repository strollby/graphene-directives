from graphql import GraphQLDirective


class DirectiveValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class DirectiveCustomValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class DirectiveInvalidTypeError(Exception):
    def __init__(self, directive: GraphQLDirective):
        message = f"Directive {str(directive)} must be build from CustomDirective(...)"
        super().__init__(message)


class DirectiveInvalidArgTypeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
