import re
from typing import Callable, Collection, Union

import graphene
from graphene import Schema as GrapheneSchema
from graphene.types.scalars import ScalarOptions
from graphene.types.union import UnionOptions
from graphene.utils.str_converters import to_camel_case, to_snake_case
from graphql import (
    DirectiveLocation,
    GraphQLArgument,
    GraphQLDirective,
    GraphQLField,
    GraphQLInputField,
    GraphQLNamedType,
    is_enum_type,
    is_input_type,
    is_interface_type,
    is_object_type,
    is_scalar_type,
    is_union_type,
    print_schema,
)
from graphql.utilities.print_schema import (
    print_args,
    print_description,
    print_directive,
    print_input_value,
)

from . import DirectiveCustomValidationError
from .data_models import SchemaDirective
from .directive import CustomDirectiveMeta
from .exceptions import DirectiveValidationError
from .parsers import (
    decorator_string,
    entity_type_to_fields_string,
    enum_type_to_fields_string,
    extend_schema_string,
    input_type_to_fields_string,
)
from .utils import (
    get_field_attribute_value,
    get_non_field_attribute_value,
    get_single_field_type,
    has_field_attribute,
    has_non_field_attribute,
)


class Schema(GrapheneSchema):
    def __init__(
        self,
        query: graphene.ObjectType = None,
        mutation: graphene.ObjectType = None,
        subscription: graphene.ObjectType = None,
        types: list[graphene.ObjectType] = None,
        directives: Union[Collection[GraphQLDirective], None] = None,
        auto_camelcase: bool = True,
        schema_directives: Collection[SchemaDirective] = None,
    ):
        self.directives = directives or []
        self.schema_directives = schema_directives or []
        self.auto_camelcase = auto_camelcase
        super().__init__(
            query=query,
            mutation=mutation,
            subscription=subscription,
            types=types,
            directives=directives,
            auto_camelcase=auto_camelcase,
        )

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

    def add_argument_decorators(
        self,
        entity_name: str,
        allowed_locations: list[str],
        required_directive_field_types: set[DirectiveLocation],
        args: dict[str, GraphQLArgument],
    ) -> str:
        if not args:
            return ""

        # If every arg does not have a description, print them on one line.
        print_single_line = not any(arg.description for arg in args.values())
        indentation: str = "  "
        new_args = []

        str_field = "(" if print_single_line else "(\n"

        for i, (name, arg) in enumerate(args.items()):
            if print_single_line:
                base_str = f"{print_input_value(name, arg)} "
            else:
                base_str = (
                    print_description(arg, f"  {indentation}", not i)
                    + f"  {indentation}"
                    + f"{print_input_value(name, arg)} "
                )
            directives = []
            for directive in self.directives:
                if has_field_attribute(arg, directive):
                    directive_values = get_field_attribute_value(arg, directive)
                    if required_directive_field_types in set(directive.locations):
                        raise DirectiveValidationError(
                            ", ".join(
                                [
                                    f"{str(directive)} cannot be used at argument {name} level",
                                    allowed_locations,
                                    f"at {entity_name}",
                                ]
                            )
                        )
                    for directive_value in directive_values:
                        directive_str = decorator_string(directive, **directive_value)
                        directives.append(directive_str)

            new_args.append(base_str + " ".join(directives))

        if print_single_line:
            str_field += ", ".join(new_args) + ")"
        else:
            str_field += "\n".join(new_args) + f"\n{indentation})"

        return str_field

    def add_field_decorators(self, graphene_types: set, string_schema: str) -> str:
        """
        For a given entity, go through all its fields and see if any directive decorator needs to be added.

        This method simply goes through the fields that need to be modified and replace them with their annotated
        version in the schema string representation.
        """

        for graphene_type in graphene_types:
            entity_name = graphene_type._meta.name  # noqa

            entity_type = self.graphql_schema.get_type(entity_name)
            get_field_graphene_type = self.field_name_to_type_attribute(graphene_type)

            required_directive_field_types = set()

            if is_object_type(entity_type) or is_interface_type(entity_type):
                required_directive_field_types.union(
                    {
                        DirectiveLocation.FIELD_DEFINITION,
                        DirectiveLocation.ARGUMENT_DEFINITION,
                    }
                )
            elif is_enum_type(entity_type):
                required_directive_field_types.add(DirectiveLocation.ENUM_VALUE)
            elif is_input_type(entity_type):
                required_directive_field_types.add(
                    DirectiveLocation.INPUT_FIELD_DEFINITION
                )
            else:
                continue

            if is_enum_type(entity_type):
                fields: dict = entity_type.values
            else:
                fields: dict = entity_type.fields

            str_fields = []
            allowed_locations = [str(t) for t in required_directive_field_types]

            for field_name, field in fields.items():
                if is_enum_type(entity_type):
                    str_field = enum_type_to_fields_string(
                        get_single_field_type(
                            entity_type, field_name, field, is_enum_type=True
                        )
                    )
                elif isinstance(field, GraphQLInputField):
                    str_field = input_type_to_fields_string(
                        get_single_field_type(entity_type, field_name, field)
                    )
                elif isinstance(field, GraphQLField):
                    str_field = entity_type_to_fields_string(
                        get_single_field_type(entity_type, field_name, field)
                    )

                    # Replace Arguments with directives
                    if hasattr(entity_type, "_fields"):
                        _arg = entity_type._fields.args[0]  # noqa
                        if hasattr(_arg, to_snake_case(field_name)):
                            arg_field = getattr(_arg, to_snake_case(field_name))
                        elif hasattr(_arg, to_camel_case(field_name)):
                            arg_field = getattr(_arg, to_camel_case(field_name))
                        else:
                            arg_field = {}

                        if (
                            hasattr(arg_field, "args")
                            and arg_field.args is not None
                            and isinstance(arg_field.args, dict)
                        ):
                            original_args = print_args(
                                args=field.args, indentation="  "
                            )
                            replacement_args = self.add_argument_decorators(
                                entity_name=entity_name,
                                allowed_locations=allowed_locations,
                                required_directive_field_types=required_directive_field_types,
                                args=arg_field.args,
                            )
                            str_field = str_field.replace(
                                original_args, replacement_args
                            )
                else:
                    continue

                # Check if we need to annotate the field by checking if it has the decorator attribute set on the field.
                field = getattr(
                    graphene_type, get_field_graphene_type(field_name), None
                )
                if field is None:
                    # Append the string, but skip the directives
                    str_fields.append(str_field)
                    continue

                for directive in self.directives:
                    if not has_field_attribute(field, directive):
                        continue
                    directive_values = get_field_attribute_value(field, directive)

                    meta_data: CustomDirectiveMeta = getattr(
                        directive, "_graphene_directive"
                    )
                    field_validator = meta_data.field_validator

                    if required_directive_field_types in set(directive.locations):
                        raise DirectiveValidationError(
                            ", ".join(
                                [
                                    f"{str(directive)} cannot be used at field level",
                                    allowed_locations,
                                    f"at {entity_name}",
                                ]
                            )
                        )
                    for directive_value in directive_values:
                        if field_validator is not None and not field_validator(
                            entity_type,
                            field,
                            {to_snake_case(k): v for k, v in directive_value.items()},
                        ):
                            raise DirectiveCustomValidationError(
                                ", ".join(
                                    [
                                        f"Custom Validation Failed for {str(directive)} with args: ({directive_value})"
                                        f"at field level {entity_name}:{field}"
                                    ]
                                )
                            )

                        str_field += (
                            f" {decorator_string(directive, **directive_value)}"
                        )

                str_fields.append(str_field)

            str_fields_annotated = "\n".join(str_fields)

            # Replace the original field declaration by the annotated one
            if is_object_type(entity_type):
                entity_type_name = "type"
                str_fields_original = entity_type_to_fields_string(entity_type)
            elif is_interface_type(entity_type):
                entity_type_name = "interface"
                str_fields_original = entity_type_to_fields_string(entity_type)
            elif is_enum_type(entity_type):
                entity_type_name = "enum"
                str_fields_original = enum_type_to_fields_string(entity_type)
            elif is_input_type(entity_type):
                entity_type_name = "input"
                str_fields_original = input_type_to_fields_string(entity_type)
            else:
                continue

            pattern = re.compile(
                r"(%s\s%s\s[^\{]*)\{\s*%s\s*\}"  # noqa
                % (entity_type_name, entity_name, re.escape(str_fields_original))
            )
            string_schema = pattern.sub(
                r"\g<1> {\n%s\n}" % str_fields_annotated, string_schema
            )
        return string_schema

    def add_non_field_decorators(
        self, non_fields_type: set[GraphQLNamedType], string_schema: str
    ) -> str:
        for non_field in non_fields_type:
            entity_name = non_field._meta.name  # noqa
            entity_type = self.graphql_schema.get_type(entity_name)

            if is_scalar_type(entity_type):
                non_field_pattern = rf"(scalar {entity_name})"
            elif is_union_type(entity_type):
                non_field_pattern = rf"(union {entity_name} )"
            elif is_object_type(entity_type):
                non_field_pattern = rf"(type {entity_name} [^\{{]*)"
            elif is_interface_type(entity_type):
                non_field_pattern = rf"(interface {entity_name} [^\{{]*)"
            elif is_enum_type(entity_type):
                non_field_pattern = rf"(enum {entity_name} [^\{{]*)"
            elif is_input_type(entity_type):
                non_field_pattern = rf"(input {entity_name} [^\{{]*)"
            else:
                continue

            directive_annotations = []
            for directive in self.directives:
                if has_non_field_attribute(non_field, directive):
                    directive_values = get_non_field_attribute_value(
                        non_field, directive
                    )
                    for directive_value in directive_values:
                        directive_annotations.append(
                            f"{decorator_string(directive, **directive_value)}"
                        )

            annotation = " ".join(directive_annotations)
            annotation = (
                f" {annotation}" if is_scalar_type(entity_type) else f"{annotation} "
            )
            replace_str = rf"\1{annotation}"
            pattern = re.compile(non_field_pattern)
            string_schema = pattern.sub(replace_str, string_schema)

        return string_schema

    def get_directive_applied_non_field_types(self) -> set:
        """
        Find all the extended types from the schema.
        They can be easily distinguished from the other type as
        the `@directive` decorator adds a `_{name}` attribute to them.
        """
        directives_types = set()
        schema_types = {
            **self.graphql_schema.type_map,
            **{
                "Query": self.graphql_schema.query_type,
                "Mutation": self.graphql_schema.mutation_type,
            },
        }

        for schema_type in schema_types.values():
            if not hasattr(schema_type, "graphene_type"):
                continue
            for directive in self.directives:
                if has_non_field_attribute(schema_type.graphene_type, directive):
                    directives_types.add(schema_type.graphene_type)
        return directives_types

    def get_directive_applied_field_types(self) -> set:
        directives_fields = set()
        schema_types = {
            **self.graphql_schema.type_map,
            **{
                "Query": self.graphql_schema.query_type,  # noqa
                "Mutation": self.graphql_schema.mutation_type,  # noqa
            },
        }

        for _, entity_type in schema_types.items():
            if (
                not hasattr(entity_type, "graphene_type")  # noqa:SIM101
                or isinstance(entity_type.graphene_type._meta, UnionOptions)  # noqa
                or isinstance(entity_type.graphene_type._meta, ScalarOptions)  # noqa
            ):
                continue

            fields = (
                list(entity_type.values.values())  # Enum class fields
                if is_enum_type(entity_type)
                else list(entity_type.fields)  # noqa
            )

            for field in fields:
                field_type = (
                    getattr(entity_type.graphene_type, to_camel_case(field), None)
                    or getattr(entity_type.graphene_type, to_snake_case(field), None)
                    if not is_enum_type(entity_type)
                    else field.value
                )
                for directive_ in self.directives:
                    if has_field_attribute(field_type, directive_):
                        directives_fields.add(entity_type.graphene_type)

                    # Handle Argument Decorators
                    if (
                        hasattr(field_type, "args")
                        and field_type.args is not None
                        and isinstance(field_type.args, dict)
                    ):
                        for arg_name, arg_type in field_type.args.items():
                            if has_field_attribute(arg_type, directive_):
                                if (
                                    DirectiveLocation.ARGUMENT_DEFINITION
                                    not in directive_.locations
                                ):
                                    raise DirectiveValidationError(
                                        f"{directive_} cannot be used at argument level at {entity_type}->{field}"
                                    )
                                directives_fields.add(entity_type.graphene_type)

        return directives_fields

    def __str__(self):
        string_schema = ""
        string_schema += extend_schema_string(string_schema, self.schema_directives)
        string_schema += print_schema(self.graphql_schema)

        field_types = self.get_directive_applied_field_types()
        non_field_types = self.get_directive_applied_non_field_types()

        string_schema = self.add_field_decorators(field_types, string_schema)
        string_schema = self.add_non_field_decorators(non_field_types, string_schema)

        for directive in self.directives:
            meta_data: CustomDirectiveMeta = getattr(directive, "_graphene_directive")
            if not meta_data.add_definition_to_schema:
                string_schema = string_schema.replace(
                    print_directive(directive) + "\n\n", ""
                )

        return string_schema.strip()
