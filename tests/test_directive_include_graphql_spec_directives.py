from pathlib import Path

import graphene
import pytest
from graphql import GraphQLArgument, GraphQLInt, GraphQLNonNull, GraphQLString

from graphene_directives import (
    CustomDirective,
    DirectiveLocation,
    DirectiveValidationError,
    build_schema,
    directive,
)

curr_dir = Path(__file__).parent


def test_pass_reserved_directive() -> None:
    with pytest.raises(DirectiveValidationError) as e_info:
        SkipDirective = CustomDirective(
            name="skip",
            locations=[
                DirectiveLocation.OBJECT,
                DirectiveLocation.INTERFACE,
                DirectiveLocation.ENUM,
                DirectiveLocation.UNION,
                DirectiveLocation.INPUT_OBJECT,
                DirectiveLocation.FIELD_DEFINITION,
                DirectiveLocation.INPUT_FIELD_DEFINITION,
                DirectiveLocation.SCALAR,
            ],
            args={
                "max_age": GraphQLArgument(
                    GraphQLNonNull(GraphQLInt),
                    description="Specifies the maximum age for cache in seconds.",
                ),
                "swr": GraphQLArgument(
                    GraphQLInt,
                    description="Stale-while-revalidate value in seconds. Optional.",
                ),
                "scope": GraphQLArgument(
                    GraphQLString, description="Scope of the cache. Optional."
                ),
            },
            description="Caching directive to control cache behavior of fields or fragments.",
        )

        @directive(target_directive=SkipDirective, max_age=500)
        class _TestClass(graphene.ObjectType):
            age = graphene.Int(required=True)
            kind = directive(
                target_directive=SkipDirective,
                field=graphene.Int(
                    required=True,
                    deprecation_reason="This field is deprecated and will be removed in future",
                ),
                max_age=500,
            )

        _ = build_schema(types=(_TestClass,), directives=(SkipDirective,))

    assert e_info.type == DirectiveValidationError


def test_pass_reserved_directive_with_disable() -> None:
    with pytest.raises(DirectiveValidationError) as e_info:
        SkipDirective = CustomDirective(
            name="skip",
            locations=[
                DirectiveLocation.OBJECT,
                DirectiveLocation.INTERFACE,
                DirectiveLocation.ENUM,
                DirectiveLocation.UNION,
                DirectiveLocation.INPUT_OBJECT,
                DirectiveLocation.FIELD_DEFINITION,
                DirectiveLocation.INPUT_FIELD_DEFINITION,
                DirectiveLocation.SCALAR,
            ],
            args={
                "max_age": GraphQLArgument(
                    GraphQLNonNull(GraphQLInt),
                    description="Specifies the maximum age for cache in seconds.",
                ),
                "swr": GraphQLArgument(
                    GraphQLInt,
                    description="Stale-while-revalidate value in seconds. Optional.",
                ),
                "scope": GraphQLArgument(
                    GraphQLString, description="Scope of the cache. Optional."
                ),
            },
            description="Caching directive to control cache behavior of fields or fragments.",
        )

        @directive(target_directive=SkipDirective, max_age=500)
        class _TestClass(graphene.ObjectType):
            age = graphene.Int(required=True)
            kind = directive(
                target_directive=SkipDirective,
                field=graphene.Int(
                    required=True,
                    deprecation_reason="This field is deprecated and will be removed in future",
                ),
                max_age=500,
            )

        _ = build_schema(
            types=(_TestClass,),
            directives=(SkipDirective,),
            include_graphql_spec_directives=True,  # default
        )

    assert e_info.type == DirectiveValidationError


def test_pass_reserved_directive_with_disable_schema() -> None:
    CacheDirective = CustomDirective(
        name="cache",
        locations=[
            DirectiveLocation.OBJECT,
            DirectiveLocation.INTERFACE,
            DirectiveLocation.ENUM,
            DirectiveLocation.UNION,
            DirectiveLocation.INPUT_OBJECT,
            DirectiveLocation.FIELD_DEFINITION,
            DirectiveLocation.INPUT_FIELD_DEFINITION,
            DirectiveLocation.SCALAR,
        ],
        args={
            "max_age": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Specifies the maximum age for cache in seconds.",
            ),
            "swr": GraphQLArgument(
                GraphQLInt,
                description="Stale-while-revalidate value in seconds. Optional.",
            ),
            "scope": GraphQLArgument(
                GraphQLString, description="Scope of the cache. Optional."
            ),
        },
        description="Caching directive to control cache behavior of fields or fragments.",
    )

    @directive(target_directive=CacheDirective, max_age=500)
    class _TestClass(graphene.ObjectType):
        age = graphene.Int(required=True)
        kind = directive(
            target_directive=CacheDirective,
            field=graphene.Int(
                required=True,
                deprecation_reason="This field is deprecated and will be removed in future",
            ),
            max_age=500,
        )

    schema = build_schema(
        types=(_TestClass,),
        directives=(CacheDirective,),
        include_graphql_spec_directives=False,
    )

    with open(
        f"{curr_dir}/schema_files/test_directive_include_graphql_spec_directives_disable.graphql",
        "w",
    ) as f:
        f.write(str(schema))

    with open(
        f"{curr_dir}/schema_files/test_directive_include_graphql_spec_directives_disable.graphql"
    ) as f:
        assert str(schema) == f.read()


def test_pass_reserved_directive_with_enable_schema() -> None:
    CacheDirective = CustomDirective(
        name="cache",
        locations=[
            DirectiveLocation.OBJECT,
            DirectiveLocation.INTERFACE,
            DirectiveLocation.ENUM,
            DirectiveLocation.UNION,
            DirectiveLocation.INPUT_OBJECT,
            DirectiveLocation.FIELD_DEFINITION,
            DirectiveLocation.INPUT_FIELD_DEFINITION,
            DirectiveLocation.SCALAR,
        ],
        args={
            "max_age": GraphQLArgument(
                GraphQLNonNull(GraphQLInt),
                description="Specifies the maximum age for cache in seconds.",
            ),
            "swr": GraphQLArgument(
                GraphQLInt,
                description="Stale-while-revalidate value in seconds. Optional.",
            ),
            "scope": GraphQLArgument(
                GraphQLString, description="Scope of the cache. Optional."
            ),
        },
        description="Caching directive to control cache behavior of fields or fragments.",
    )

    @directive(target_directive=CacheDirective, max_age=500)
    class _TestClass(graphene.ObjectType):
        age = graphene.Int(required=True)
        kind = directive(
            target_directive=CacheDirective,
            field=graphene.Int(
                required=True,
                deprecation_reason="This field is deprecated and will be removed in future",
            ),
            max_age=500,
        )

    schema = build_schema(
        types=(_TestClass,),
        directives=(CacheDirective,),
        include_graphql_spec_directives=True,  # default
    )

    with open(
        f"{curr_dir}/schema_files/test_directive_include_graphql_spec_directives.graphql",
        "w",
    ) as f:
        f.write(str(schema))

    with open(
        f"{curr_dir}/schema_files/test_directive_include_graphql_spec_directives.graphql"
    ) as f:
        assert str(schema) == f.read()
