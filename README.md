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

## Example

### Using `@directive`

```python
import graphene
from graphql import (
    DirectiveLocation,
    GraphQLArgument,
    GraphQLDirective,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_directives import build_schema, directive

CacheDirective = GraphQLDirective(
    name="cache",
    locations=[DirectiveLocation.FIELD, DirectiveLocation.OBJECT],
    args={
        "maxAge": GraphQLArgument(
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


### Using `@build_decorator_from_directive`

```python
import graphene
from graphql import (
    DirectiveLocation,
    GraphQLArgument,
    GraphQLDirective,
    GraphQLInt,
    GraphQLNonNull,
    GraphQLString,
)

from graphene_directives import build_decorator_from_directive, build_schema

CacheDirective = GraphQLDirective(
    name="cache",
    locations=[DirectiveLocation.FIELD, DirectiveLocation.OBJECT],
    args={
        "maxAge": GraphQLArgument(
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
cache = build_decorator_from_directive(target_directive=CacheDirective)


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