# Graphene Directives
Schema Directives implementation for graphene

[![PyPI version][pypi-image]][pypi-url]
[![PyPI pyversions][pypi-version-image]][pypi-version-url]
[![Downloads][pypi-downloads-image]][pypi-downloads-url]
[![Test Status][tests-image]][tests-url]
[![Coverage Status][coveralls-image]][coveralls-url]

[pypi-image]: https://badge.fury.io/py/graphene-directives.svg
[pypi-url]: https://pypi.org/project/graphene-directives/
[pypi-version-image]: https://img.shields.io/pypi/pyversions/graphene-directives.svg
[pypi-version-url]: https://pypi.python.org/pypi/graphene-directives/
[pypi-downloads-image]: https://pepy.tech/badge/graphene-directives
[pypi-downloads-url]: https://pepy.tech/project/graphene-directives
[tests-image]: https://github.com/strollby/graphene-directives/actions/workflows/test.yml/badge.svg?branch=main
[tests-url]: https://github.com/strollby/graphene-directives/actions/workflows/test.yml
[coveralls-image]: https://coveralls.io/repos/github/strollby/graphene-directives/badge.svg?branch=main
[coveralls-url]: https://coveralls.io/github/strollby/graphene-directives?branch=main

------------------------

## Directive Locations Supported

- [x] DirectiveLocation.SCHEMA
- [x] DirectiveLocation.OBJECT
- [x] DirectiveLocation.ENUM
- [x] DirectiveLocation.INTERFACE
- [x] DirectiveLocation.UNION
- [x] DirectiveLocation.SCALAR
- [x] DirectiveLocation.FIELD_DEFINITION
- [x] DirectiveLocation.INPUT_FIELD_DEFINITION
- [x] DirectiveLocation.INPUT_OBJECT
- [x] DirectiveLocation.ENUM_VALUE
- [x] DirectiveLocation.ARGUMENT_DEFINITION,

------------------------

## Example

### Using `@directive`

```python
import graphene
from graphql import (
    GraphQLArgument,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_directives import CustomDirective, DirectiveLocation, build_schema, directive

CacheDirective = CustomDirective(
    name="cache",
    locations=[DirectiveLocation.FIELD_DEFINITION, DirectiveLocation.OBJECT],
    args={
        "max_age": GraphQLArgument(
            GraphQLNonNull(GraphQLInt),
            description="Specifies the maximum age for cache in seconds.",
        ),
        "swr": GraphQLArgument(
            GraphQLInt, description="Stale-while-revalidate value in seconds. Optional."
        ),
        "scope": GraphQLArgument(
            GraphQLString, description="Scope of the cache. Optional."
        ),
    },
    description="Caching directive to control cache behavior of fields or fragments.",
)


@directive(CacheDirective, max_age=200)
class SomeType(graphene.ObjectType):
    field_1 = directive(CacheDirective, field=graphene.String(), max_age=300)
    field_2 = directive(CacheDirective, field=graphene.String(), max_age=300, swr=2)
    field_3 = graphene.String()


class Query(graphene.ObjectType):
    some_query = graphene.Field(SomeType)


schema = build_schema(
    query=Query, directives=[CacheDirective]
) 
```


### Using `directive_decorator`

```python
import graphene
from graphql import (
    GraphQLArgument,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_directives import CustomDirective, DirectiveLocation, build_schema, directive_decorator

CacheDirective = CustomDirective(
    name="cache",
    locations=[DirectiveLocation.FIELD_DEFINITION, DirectiveLocation.OBJECT],
    args={
        "max_age": GraphQLArgument(
            GraphQLNonNull(GraphQLInt),
            description="Specifies the maximum age for cache in seconds.",
        ),
        "swr": GraphQLArgument(
            GraphQLInt, description="Stale-while-revalidate value in seconds. Optional."
        ),
        "scope": GraphQLArgument(
            GraphQLString, description="Scope of the cache. Optional."
        ),
    },
    description="Caching directive to control cache behavior of fields or fragments.",
)

# This returns a partial of directive function
cache = directive_decorator(target_directive=CacheDirective)


@cache(max_age=200)
class SomeType(graphene.ObjectType):
    field_1 = cache(field=graphene.String(), max_age=300)
    field_2 = cache(field=graphene.String(), max_age=300, swr=2)
    field_3 = graphene.String()


class Query(graphene.ObjectType):
    some_query = graphene.Field(SomeType)


schema = build_schema(
    query=Query, directives=[CacheDirective]
)
```

### Custom Input Validation

```python
from typing import Any

import graphene
from graphql import (
    GraphQLArgument,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_directives import CustomDirective, DirectiveLocation, Schema, build_schema, directive_decorator


def input_transform(inputs: dict, _schema: Schema) -> dict:
    """
    def input_transform (inputs: Any, schema: Schema) -> dict,
    """
    if inputs.get("max_age") > 200:
        inputs["swr"] = 30
    return inputs


def validate_non_field_input(_type: Any, inputs: dict, _schema: Schema) -> bool:
    """
    def validator (type_: graphene type, inputs: Any, schema: Schema) -> bool,
    if validator returns False, library raises DirectiveCustomValidationError
    """
    if inputs.get("max_age") > 2500:
        return False
    return True


def validate_field_input(
        _parent_type: Any, _field_type: Any, inputs: dict, _schema: Schema
) -> bool:
    """
    def validator (parent_type_: graphene_type, field_type_: graphene type, inputs: Any, schema: Schema) -> bool,
    if validator returns False, library raises DirectiveCustomValidationError
    """
    if inputs.get("max_age") > 2500:
        return False
    return True


CacheDirective = CustomDirective(
    name="cache",
    locations=[DirectiveLocation.FIELD_DEFINITION, DirectiveLocation.OBJECT],
    args={
        "max_age": GraphQLArgument(
            GraphQLNonNull(GraphQLInt),
            description="Specifies the maximum age for cache in seconds.",
        ),
        "swr": GraphQLArgument(
            GraphQLInt, description="Stale-while-revalidate value in seconds. Optional."
        ),
        "scope": GraphQLArgument(
            GraphQLString, description="Scope of the cache. Optional."
        ),
    },
    description="Caching directive to control cache behavior of fields or fragments.",
    non_field_validator=validate_non_field_input,
    field_validator=validate_field_input,
    input_transform=input_transform,
)

# This returns a partial of directive function
cache = directive_decorator(target_directive=CacheDirective)


@cache(max_age=200)
class SomeType(graphene.ObjectType):
    field_1 = cache(field=graphene.String(), max_age=300)
    field_2 = cache(field=graphene.String(), max_age=300, swr=2)
    field_3 = graphene.String()


class Query(graphene.ObjectType):
    some_query = graphene.Field(SomeType)


schema = build_schema(
    query=Query, directives=[CacheDirective]
)
```


### Complex Use Cases

Refer [`Code`](./example/complex_uses.py) and [`Graphql Output`](./example/complex_uses.graphql)
