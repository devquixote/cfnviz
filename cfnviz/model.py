from collections import namedtuple
from collections import defaultdict

from recordclass import recordclass

Parameter = namedtuple("Parameter", ["name", "type"])
Mapping = recordclass("Mapping", ["key", "value"])
Condition = namedtuple("Condition", ["name"])
Output = namedtuple("Output", ["name"])
Resource = recordclass("Resource", ["name", "type", "attributes"])
Attribute = recordclass("Attribute", ["name", "refers_to"])
Edge = namedtuple("Edge", ["source", "dest"])


class Model(object):
    def __init__(self, file_name=None, description=None):
        self.file_name = file_name
        self.description = description
        self.parameters = []
        self.mappings = []
        self.conditions = []
        self.outputs = []
        self.resources = defaultdict(
            lambda: Resource(
              None, None, defaultdict(lambda: Attribute(None, set()))))
        self.resource_edges = set()
