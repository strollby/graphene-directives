import re
from typing import Collection, Any, Callable

import graphene
from graphene import Schema as GrapheneSchema
from graphene.types.union import UnionOptions
from graphene.utils.str_converters import to_camel_case
from graphql import (
    print_schema,
    GraphQLObjectType,
    GraphQLInterfaceType,
    GraphQLDirective,
    DirectiveLocation,
)
from graphql.utilities.print_schema import print_fields  # noqa
from graphene.types.enum import EnumOptions
from graphene.types.scalars import ScalarOptions


class MonoFieldType:
    """
    In order to be able to reuse the `print_fields` method to get a singular field
    string definition, we need to define an object that has a `.fields` attribute.
    """

    def __init__(self, name, field) -> None:  # noqa
        self.fields = {name: field}


class Schema(GrapheneSchema):
    def __init__(
        self,
        query: graphene.ObjectType = None,
        mutation: graphene.ObjectType = None,
        subscription: graphene.ObjectType = None,
        types: list[graphene.ObjectType] = None,
        directives: Collection[GraphQLDirective] | None = None,
        auto_camelcase: bool = True,
    ):
        self.directives = directives or []
        super().__init__(
            query=query,
            mutation=mutation,
            subscription=subscription,
            types=types,
            directives=directives,
            auto_camelcase=auto_camelcase,
        )

    def decorator_resolver(self, directive, **kwargs):  # noqa
        # Extract directive name
        directive_name = directive.name

        # Format each keyword argument as a string, considering its type
        formatted_args = [
            f'{to_camel_case(key)}: {"\"" + str(value) + "\"" if isinstance(value, str) else value}'
            for key, value in kwargs.items()
            if value is not None and to_camel_case(key) in directive.args
        ]

        # Construct the directive string
        return f"@{directive_name}({', '.join(formatted_args)})"

    def field_name_to_type_attribute(
        self, model: graphene.ObjectType
    ) -> Callable[[str], str]:
        """
        Create field name conversion method (from schema name to actual graphene_type attribute name).
        """
        field_names = {}
        if self.auto_camelcase:
            field_names = {
                to_camel_case(attr_name): attr_name
                for attr_name in getattr(model._meta, "fields", [])  # noqa
            }
        return lambda schema_field_name: field_names.get(
            schema_field_name, schema_field_name
        )

    def type_attribute_to_field_name(self) -> Callable[[str], str]:
        """
        Create a conversion method to convert from graphene_type attribute name to the schema field name.
        """
        if self.auto_camelcase:
            return lambda attr_name: to_camel_case(attr_name)
        return lambda attr_name: attr_name

    def convert_fields(self, fields: list[str]) -> str:
        get_field_name = self.type_attribute_to_field_name()
        return " ".join([get_field_name(field) for field in fields])

    @staticmethod
    def field_to_string(field: GraphQLObjectType | GraphQLInterfaceType) -> str:
        str_field = print_fields(field)
        # Remove blocks added by `print_block`
        block_match = re.match(
            r" \{\n(?P<field_str>.*)\n\}",
            str_field,
            flags=re.DOTALL,  # noqa
        )
        if block_match:
            str_field = block_match.groups()[0]
        return str_field

    def add_type_fields_decorators(self, types_: set, string_schema: str) -> str:
        """
        For a given entity, go through all its fields and see if any directive decorator need to be added.
        The methods (from graphene-federation) marking fields that require some special treatment for federation add
        corresponding attributes to the field itself.
        Those attributes are listed in the `DECORATORS` variable as key and their respective value is the resolver that
        returns what needs to be amended to the field declaration.

        This method simply go through the fields that need to be modified and replace them with their annotated
        version in the schema string representation.
        """
        for type_ in types_:
            entity_name = type_._meta.name  # noqa
            entity_type = self.graphql_schema.get_type(entity_name)
            str_fields = []
            get_model_attr = self.field_name_to_type_attribute(type_)
            for field_name, field in (
                entity_type.fields.items()
                if getattr(entity_type, "fields", None)
                else []
            ):
                str_field = self.field_to_string(MonoFieldType(field_name, field))  # noqa
                # Check if we need to annotate the field by checking if it has the decorator attribute set on the field.
                f = getattr(type_, get_model_attr(field_name), None)
                if f is not None:
                    for directive in self.directives:
                        decorator_value = getattr(f, f"_{directive.name}", None)
                        if decorator_value:
                            if DirectiveLocation.FIELD not in directive.locations:
                                raise ValueError("Directive not supported on fields")
                            str_field += f" {self.decorator_resolver(directive, **decorator_value)}"
                str_fields.append(str_field)
            str_fields_annotated = "\n".join(str_fields)
            # Replace the original field declaration by the annotated one
            if isinstance(entity_type, GraphQLObjectType) or isinstance(  # noqa
                entity_type, GraphQLInterfaceType
            ):
                str_fields_original = self.field_to_string(entity_type)
            else:
                str_fields_original = ""
            pattern = re.compile(
                r"(type\s%s\s[^\{]*)\{\s*%s\s*\}"  # noqa
                % (entity_name, re.escape(str_fields_original))
            )
            string_schema = pattern.sub(
                r"\g<1> {\n%s\n}" % str_fields_annotated, string_schema
            )
        return string_schema

    def add_type_decorators(self, types_: set, string_schema: str) -> str:
        for type_ in types_:
            # noinspection PyProtectedMember
            if isinstance(type_._meta, UnionOptions):
                type_def_re = rf"(union {type_._meta.name} )"  # noqa
            else:
                type_def_re = rf"(type {type_._meta.name} [^\{{]*)"  # noqa
            type_annotation = ""
            for directive in self.directives:
                decorator_value = getattr(type_, f"_{directive.name}", None)
                if decorator_value:
                    if DirectiveLocation.OBJECT not in directive.locations:
                        raise ValueError("Directive not supported on fragments")
                    type_annotation += (
                        f"{self.decorator_resolver(directive, **decorator_value)}"
                    )

            repl_str = rf"\1{type_annotation} "
            pattern = re.compile(type_def_re)
            string_schema = pattern.sub(repl_str, string_schema)
        return re.sub(r"[ ]+", " ", string_schema)  # noqa

    def get_directive_types(self) -> set:
        """
        Find all the extended types from the schema.
        They can be easily distinguished from the other type as
        the `@directive` decorator adds a `_{name}` attribute to them.
        """
        directives_types = set()
        for type_name, type_ in self.graphql_schema.type_map.items():
            if not hasattr(type_, "graphene_type"):
                continue
            for directive_ in self.directives:
                if getattr(
                    type_.graphene_type,
                    f"_{directive_.name}",
                    False,  # noqa
                ):
                    directives_types.add(type_.graphene_type)
        return directives_types

    def get_directive_fields(self) -> set[Any]:
        directives_fields = set()
        for type_name, type_ in self.graphql_schema.type_map.items():
            if (
                not hasattr(type_, "graphene_type")  # noqa
                or isinstance(type_.graphene_type._meta, UnionOptions)  # noqa
                or isinstance(type_.graphene_type._meta, ScalarOptions)  # noqa
                or isinstance(type_.graphene_type._meta, EnumOptions)  # noqa
            ):
                continue
            for directive_ in self.directives:
                for field in list(type_.graphene_type._meta.fields):  # noqa
                    if getattr(
                        getattr(type_.graphene_type, field, None),
                        f"_{directive_.name}",
                        False,
                    ):
                        directives_fields.add(type_.graphene_type)
        return directives_fields

    def __str__(self):
        string_schema = print_schema(self.graphql_schema)
        regex = r"schema \{(\w|\!|\s|\:)*\}"
        pattern = re.compile(regex)
        string_schema = pattern.sub(" ", string_schema)

        string_schema = self.add_type_fields_decorators(
            self.get_directive_fields(), string_schema
        )
        string_schema = self.add_type_decorators(
            self.get_directive_types(), string_schema
        )
        return re.sub(r"[ ]+", " ", string_schema)  # noqa
