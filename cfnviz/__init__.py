import json
import yaml

from cfnviz.factories import ModelFactory
from cfnviz.renderers import DotRenderer


def default_ctor(loader, tag_suffix, node):
    return "{} {}".format(tag_suffix, node.value)


yaml.add_multi_constructor("", default_ctor)


def parse_document(input):
    try:
        return json.loads(input)
    except ValueError:
        return yaml.load(input)


def build_model(document):
    return ModelFactory(document)()


def to_dot(model):
    return DotRenderer(model)()
