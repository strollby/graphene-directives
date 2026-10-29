import graphene
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull

from graphene_directives import (
    CustomDirective,
    DirectiveLocation,
    Schema,
    build_schema,
    directive,
)

CacheDirective = CustomDirective(
    name="cache",
    locations=[DirectiveLocation.OBJECT, DirectiveLocation.FIELD_DEFINITION],
    args={
        "max_age": GraphQLArgument(
            GraphQLNonNull(GraphQLInt),
            description="Specifies the maximum age for cache in seconds.",
        )
    },
    description="Caching directive.",
)


@directive(target_directive=CacheDirective, max_age=100)
class _CachedType(graphene.ObjectType):
    name = graphene.String(required=True)


class _Query(graphene.ObjectType):
    cached = graphene.Field(_CachedType)


def test_default_schema() -> None:
    schema = build_schema(query=_Query, directives=(CacheDirective,))
    assert isinstance(schema, Schema)
    assert type(schema) is Schema


def test_custom_schema_factory_returns_subclass_instance() -> None:
    class CustomSchema(Schema):
        pass

    schema = build_schema(
        query=_Query, directives=(CacheDirective,), schema_factory=CustomSchema
    )
    assert isinstance(schema, Schema)
    assert isinstance(schema, CustomSchema)
    assert type(schema) is CustomSchema


def test_custom_schema_factory_produces_same_output_as_default() -> None:
    class CustomSchema(Schema):
        pass

    default_schema = build_schema(query=_Query, directives=(CacheDirective,))
    custom_schema = build_schema(
        query=_Query, directives=(CacheDirective,), schema_factory=CustomSchema
    )
    assert str(default_schema) == str(custom_schema)
