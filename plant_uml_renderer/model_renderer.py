import os
from enum import Enum
from subprocess import call

from codeable_models import *
from codeable_models.internal.commons import set_keyword_args, is_cobject


class RenderingContext(object):
    def __init__(self):
        super().__init__()
        self.result = ""
        self.indent = 0
        self.indent_cache_string = ""
        self.unnamed_objects = {}
        self.unnamed_id = 0

    def get_unnamed_celement_id(self, element):
        if is_cobject(element) and element.class_object_class_ is not None:
            # use the class object's class rather than the class object to identify them uniquely
            element = element.class_object_class_
        if element in self.unnamed_objects:
            return self.unnamed_objects[element]
        else:
            self.unnamed_id += 1
            name = f"__{self.unnamed_id!s}"
            self.unnamed_objects[element] = name
            return name

    def add_line(self, string):
        self.result += self.indent_cache_string + string + "\n"

    def add_with_indent(self, string):
        self.result += self.indent_cache_string + string

    def add(self, string):
        self.result += string

    def increase_indent(self):
        self.indent += 2
        self.indent_cache_string = " " * self.indent

    def decrease_indent(self):
        self.indent -= 2
        self.indent_cache_string = " " * self.indent


class ModelStyle(Enum):
    PLAIN = 0
    HANDWRITTEN = 1
    ORIGINAL = 2


class ModelRenderer(object):
    def __init__(self, **kwargs):
        # defaults for config parameters
        self.directory = "./gen"
        self.plant_uml_jar_path = "../libs/plantuml.jar"
        self.render_png = True
        self.render_svg = True

        self.name_break_length = 25
        self.name_padding = ""
        self.style = ModelStyle.PLAIN
        self.left_to_right = False

        self.ID = 0

        super().__init__()
        self._init_keyword_args(**kwargs)

    def _init_keyword_args(self, legal_keyword_args=None, **kwargs):
        if legal_keyword_args is None:
            legal_keyword_args = ["directory", "plant_uml_jar_path", "genSVG", "genPNG"]
        set_keyword_args(self, legal_keyword_args, **kwargs)

    def render_start_graph(self, context):
        context.add_line("@startuml")
        if self.style == ModelStyle.HANDWRITTEN or self.style == ModelStyle.PLAIN:
            context.add_line("skinparam monochrome true")
            context.add_line("skinparam ClassBackgroundColor White")
            context.add_line("hide empty members")
            context.add_line("hide circle")
            if self.style == ModelStyle.HANDWRITTEN:
                # context.addLine("skinparam defaultFontName MV Boli")
                context.add_line("skinparam defaultFontName Segoe Print")
                context.add_line("skinparam defaultFontSize 14")
                context.add_line("skinparam handwritten true")
                context.add_line("skinparam shadowing false")
            if self.style == ModelStyle.PLAIN:
                context.add_line("skinparam defaultFontName Arial")
                context.add_line("skinparam defaultFontSize 11")
                context.add_line("skinparam classfontstyle bold")
        if self.left_to_right:
            context.add_line("left to right direction")

    @staticmethod
    def render_end_graph(context):
        context.add_line("@enduml")

    def render_stereotypes_string(self, stereotypes_string):
        return "«" + self.break_name(stereotypes_string) + "»\\n"

    def render_stereotypes(self, stereotyped_element_instance, stereotypes):
        if len(stereotypes) == 0:
            return ""

        result = "«"
        tagged_values_string = "\\n{"
        rendered_tagged_values = []

        first_stereotype = True
        for stereotype in stereotypes:
            if first_stereotype:
                first_stereotype = False
            else:
                result += ", "

            stereotype_class_path = stereotype.class_path

            for stereotypeClass in stereotype_class_path:
                for taggedValue in stereotypeClass.attributes:
                    if not [taggedValue.name, stereotypeClass] in rendered_tagged_values:
                        value = stereotyped_element_instance.get_tagged_value(taggedValue.name, stereotypeClass)
                        if value is not None:
                            if len(rendered_tagged_values) != 0:
                                tagged_values_string += ", "
                            tagged_values_string += self.render_attribute_value(taggedValue, taggedValue.name, value)
                            rendered_tagged_values.append([taggedValue.name, stereotypeClass])

            result += stereotype.name

        result = self.break_name(result)

        if len(rendered_tagged_values) != 0:
            tagged_values_string += "}"
        else:
            tagged_values_string = ""
        result += "» " + tagged_values_string
        result += "\\n"
        return result

    def render_attribute_values(self, context, obj):
        if not context.render_attribute_values:
            return ""
        attribute_value_added = False
        attribute_value_string = " {\n"
        rendered_attributes = set()
        for cl in obj.classifier.class_path:
            attributes = cl.attributes
            for attribute in attributes:
                name = attribute.name
                value = obj.get_value(name, cl)

                # don't render the same attribute twice, but only the one that is lowest in the class hierarchy
                if name in rendered_attributes:
                    continue
                else:
                    rendered_attributes.add(name)

                if not context.render_empty_attributes:
                    if value is None:
                        continue
                attribute_value_added = True
                attribute_value_string += self.render_attribute_value(attribute, name, value) + "\n"
        attribute_value_string += "}\n"
        if not attribute_value_added:
            attribute_value_string = ""
        return attribute_value_string

    def render_attribute_value(self, attribute, name, value):
        type_ = attribute.type
        if type_ == str:
            value = '"' + str(value) + '"'
        elif type_ == list and value is not None:
            result = []
            for elt in value:
                if isinstance(elt, str):
                    result.append('"' + str(elt) + '"')
                else:
                    result.append(str(elt))
            value = "[" + ", ".join(result) + "]"
        _check_for_illegal_value_characters(str(value))
        return self.break_name(name + ' = ' + str(value))

    def pad_and_break_name(self, name, name_padding=None):
        if name_padding is None:
            name_padding = self.name_padding

        if len(name) <= self.name_break_length:
            return name_padding + name + name_padding

        result = ""
        count = 0
        current_first_index = 0
        for i, v in enumerate(name):
            if v == ' ' and count >= self.name_break_length:
                if name[i - 1] == ':':
                    # we don't want to end the line with a ':', break on next occasion
                    continue
                if i + 1 < len(name) and name[i + 1] == '=':
                    # we don't want to break if the next line starts with '=' as this leads to some 
                    # undocumented font size increase in plant uml, break on next occasion
                    continue
                count = 0
                result = result + name_padding + name[current_first_index:i] + name_padding + "\\n"
                current_first_index = i + 1
            count += 1
        result = result + name_padding + name[current_first_index:len(name)] + name_padding
        return result

    def break_name(self, name):
        return self.pad_and_break_name(name, "")

    @staticmethod
    def get_node_id(context, element):
        if isinstance(element, CNamedElement):
            name = element.name
            if name is None:
                name = context.get_unnamed_celement_id(element)
        else:
            # else this must be a string
            name = element

        # we add a "_" before the name to make sure the name is not a plantuml keyword
        name = f"_{name!s}"

        # put a placeholder in the name for special characters as plantuml does not
        # support many of them
        name = "".join([c if c.isalnum() else "_" + str(ord(c)) + "_" for c in name])
        return name

    def render_to_files(self, file_name_base, source):
        file_name_base_with_dir = f"{self.directory!s}/{file_name_base!s}"
        file_name_txt = file_name_base_with_dir + ".txt"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        file = open(file_name_txt, "w")
        file.write(source)
        file.close()
        if self.render_png:
            call(["java", "-jar", f"{self.plant_uml_jar_path!s}", f"{file_name_txt!s}"])
        if self.render_svg:
            call(["java", "-jar", f"{self.plant_uml_jar_path!s}", f"{file_name_txt!s}", "-tsvg"])


def _check_for_illegal_value_characters(value):
    if '(' in value or ')' in value:
        raise CException(
            "do not use '(' or ')' in attribute values, as PlantUML interprets them as method parameters " +
            "and would start a new compartment if they are part of an attribute value")
