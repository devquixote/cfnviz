import re

from cfnviz.model import Parameter
from cfnviz.model import Mapping
from cfnviz.model import Condition
from cfnviz.model import Output
from cfnviz.model import Attribute
from cfnviz.model import Edge
from cfnviz.model import Model


def visit(value, fn, context={"path": []}):
    path = context.get("path")
    context["parent"] = path[-1] if path else None

    fn(value, context)

    if type(value) is list:
        for child in value:
            visit(child, fn, context)
    elif type(value) is dict:

        for name, child in value.iteritems():
            context["name"] = name
            context["path"].append(name)

            visit(child, fn, context)
            context["path"].pop()
    else:
        return


def str_list_values(str):
    results = []
    matches = re.findall(".*\[(.*?)\].*", str)

    if matches:
        match = matches[0].strip()
        results = [element.strip() for element in match.split(",")]

    return results


invalid_name_patterns = ("^Fn::.*", "Ref", "![a-zA-Z]+ .*", "Value")


def find_first_valid_name(path):
    for element in path[::-1]:
        valid_name = element
        for pattern in invalid_name_patterns:
            if re.match(pattern, element):
                valid_name = None
                break
        if valid_name:
            return valid_name


def collect_references(str):
    capturing = False
    previous_char = None
    reference = ""
    references = []

    for current_char in str:
        if not capturing and previous_char == "$" and current_char == "{":
            capturing = True
        elif capturing and current_char == "}":
            references.append(reference)
            reference = ""
            capturing = False
        elif capturing:
            reference = reference + current_char
        previous_char = current_char

    return references


class ModelFactory(object):
    def __init__(self, document):
        self.document = document

    def __call__(self):
        # TODO document needs file name
        self.model = Model(description=self.document.get("Description"))

        self.collect_parameters()
        self.collect_mappings()
        self.collect_conditions()
        self.collect_outputs()
        self.collect_resources()
        self.collect_edges()

        return self.model

    def collect_edges(self):
        for resource in self.model.resources.values():
            for attribute in resource.attributes.values():
                for reference in attribute.refers_to:
                    dest = reference.split(".")[0]
                    if dest in self.model.resources:
                        edge = Edge(resource.name, dest)
                        self.model.resource_edges.add(edge)

    def collect_parameters(self):
        if self.document.get("Parameters"):
            self.model.parameters = [Parameter(name, doc["Type"]) for name, doc
                                     in self.document["Parameters"]
                                     .iteritems()]

    def collect_mappings(self):
        if self.document.get("Mappings"):
            model = self.model

            def parse_mapping(value, context):
                if not context.get("parsing"):
                    context["mapping"] = Mapping([], None)
                    context["parsing"] = True
                elif isinstance(value, (tuple, list, set, dict)):
                    context["mapping"].key.append(context["name"])
                else:
                    context["mapping"].key = ".".join(context["path"])
                    context["mapping"].value = value
                    model.mappings.append(context["mapping"])
                    context["parsing"] = False

            visit(self.document["Mappings"], parse_mapping)

    def collect_conditions(self):
        if self.document.get("Conditions"):
            self.model.conditions = [Condition(name) for name
                                     in self.document["Conditions"].keys()]

    def collect_outputs(self):
        if self.document.get("Outputs"):
            self.model.outputs = [Output(name) for name
                                  in self.document["Outputs"].keys()]

    @property
    def collect_resources(self):
        return ResourceFactory(self.model, self.document.get('Resources'))


class ResourceFactory(object):
    def __init__(self, model, document):
        self.model = model
        self.document = document

    def __call__(self):
        if not self.document:
            return

        model = self.model

        def collector(value, context):
            path = context.get("path")
            # name = context.get("name")
            name = find_first_valid_name(path)
            parent = context.get("parent")
            resource = context.get("resource")
            attr = context.get("attr")

#            if path and "Fn::GetAtt" in path:
#                from pdb import set_trace
#                set_trace()

            try:
                if len(path) == 1:
                    model.resources[name].name = name
                    model.resources[name].type = value.get("Type")
                    context["resource"] = model.resources[name]
                elif "Ref" in path:
                    attr = resource.attributes[name]
                    attr.name = name
                    attr.refers_to.add(value)
                elif parent == "Fn::GetAtt" and type(value) is list:
                    attr = resource.attributes[name]
                    attr.name = name
                    attr.refers_to.add(".".join(value))
                elif type(value) is str and "FindInMap" in value:
                    # TODO this is currently confuckled because pyaml is
                    # decoding elements of !FindInMap [ Foo, Bar ] as
                    # ScalarNodes.  Need to fix eventually.
                    map_path = str_list_values(value)
                    if map_path:
                        attr = resource.attributes[name]
                        attr.name = name
                        attr.refers_to.add(".".join(map_path))
                elif type(value) is str and "GetAtt" in value:
                    attr = resource.attributes[name]
                    attr.name = name
                    attr.refers_to.add(value.split()[-1])
                elif type(value) is str and "Sub" in value:
                    references = collect_references(value)
                    if references:
                        attr = resource.attributes[name]
                        attr.name = name
                        attr.refers_to.update(references)
                else:
                    attr = context["attr"] = Attribute(name, [])
            except Exception as e:
                print e
                from pdb import set_trace
                set_trace()

        visit(self.document, collector, {"path": []})
