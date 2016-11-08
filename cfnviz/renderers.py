
default_values = {
    "ranksep": "0.4",
    "nodesep": "0.4",
    "font": "arial",
    "bold_font": "arial bold",
    "fontcolor": "grey15",
    "edgecolor": "grey15",
    "clear": "white"
}

digraph_template = """
digraph cfn_template {{
  graph [
    rankdir="TB";
    fontname="{font}";
  ]
  concentrate=true;
  ratio=compress;
  ranksep="{ranksep}";
  nodesep="{nodesep}";

  node [shape=box,fontname="{font}",fontcolor="{fontcolor}"];
  edge [arrowhead="vee",color="{edgecolor}"];

  subgraph everything_but_resources {{
    color="{clear}";

    {outputs_cluster}

    {conditions_cluster}

    {mappings_cluster}

    {parameters_cluster}

    {non_resource_edges}  [style=invis]
  }}


  {resources_cluster}

}}
"""

subgraph_template = """
    subgraph cluster_{label} {{
      label="{label}";
      fontsize="36";
      fontcolor="grey35";
      color="{clear}";

      node [fontsize=14, shape=record]

      {element_type} [
        label="{{{elements}}}";
      ]
    }}
"""


resource_subgraph_template = """
  subgraph cluster_resources {{
    label="Resources";
    fontsize="36";
    fontname="{font}";
    fontcolor="grey35";
    color="{clear}";

    node [fontsize=14, shape=none]

    {resource_nodes}

    {resource_edges}

  }}
"""

resource_type_row_view = '''
          <TR>
            <TD BORDER="0" BGCOLOR="{clear}" COLSPAN="2"><FONT POINT-SIZE="10">{type_path}</FONT><BR/>{type}</TD>
          </TR>
'''

resource_name_row_view = '''
          <TR>
            <TD BORDER="0" CELLPADDING="10" COLSPAN="2"><FONT POINT-SIZE="28" FACE="{bold_font}" COLOR="{clear}">{name}</FONT></TD>
          </TR>
'''

resource_attribute_row_view = '''
          <TR>
            <TD BORDER="0" BGCOLOR="{clear}" VALIGN="top" ALIGN="RIGHT">{name}:</TD>
            <TD BORDER="0" BGCOLOR="{clear}" ALIGN="LEFT">{values}</TD>
          </TR>
'''

resource_node_view = '''
    {name} [
      label=<
        <TABLE BORDER="1" BGCOLOR="grey65" COLOR="grey15" CELLPADDING="3" CELLSPACING="0">
          {type_row}
          {name_row}
          {attribute_rows}
        </TABLE>
      >
    ]
'''


class DotRenderer(object):
    def __init__(self, model):
        self.model = model

    def __call__(self):
        output_names = [output.name for output in self.model.outputs]
        condition_names = [cond.name for cond in self.model.conditions]
        mapping_keys = [mapping.key for mapping in self.model.mappings]
        parameter_names = [param.name for param in self.model.parameters]

        context = default_values.copy()
        context['outputs_cluster'] = self.__render_subgraph(
            "Outputs", "Outputs", output_names)
        context['conditions_cluster'] = self.__render_subgraph(
            "Conditions", "Conditions", condition_names)
        context['mappings_cluster'] = self.__render_subgraph(
            "Mappings", "Mappings", mapping_keys)
        context['parameters_cluster'] = self.__render_subgraph(
            "Parameters", "Parameters", parameter_names)
        context['non_resource_edges'] = self.__render_non_resource_edges()
        context['resources_cluster'] = self.__render_resources_subgraph()

        return digraph_template.format(**context)

    def __render_non_resource_edges(self):
        # Parameters -> Mappings -> Conditions -> Outputs [style=invis]
        elements = []

        if self.model.parameters:
            elements.append('Parameters')
        if self.model.mappings:
            elements.append('Mappings')
        if self.model.conditions:
            elements.append('Conditions')
        if self.model.outputs:
            elements.append('Outputs')

        return " -> ".join(elements)

    def __render_resources_subgraph(self):
        context = default_values.copy()
        context['resource_nodes'] = self.__render_resources()
        context['resource_edges'] = self.__render_edges()
        return resource_subgraph_template.format(**context)

    def __render_resources(self):
        renderings = []
        model = self.model

        for resource in sorted(self.model.resources.values(),
                               key=lambda resource: len(resource.attributes)):
            context = default_values.copy()
            context['name'] = resource.name
            context['type_row'] = self.__render_type_row(resource.type)
            context['name_row'] = self.__render_name_row(resource.name)
            context['attribute_rows'] = self.__render_attribute_rows(
                resource.attributes)

            renderings.append(resource_node_view.format(**context))

        return "\n".join(renderings)

    def __render_type_row(self, resource_type):
        context = default_values.copy()
        type_elements = resource_type.split("::")
        context['type'] = type_elements.pop()
        context['type_path'] = "::".join(type_elements)

        return resource_type_row_view.format(**context)

    def __render_name_row(self, resource_name):
        context = default_values.copy()
        context['name'] = resource_name

        return resource_name_row_view.format(**context)

    def __render_attribute_rows(self, attributes):
        rows = []

        for attribute in attributes.values():
            context = default_values.copy()
            context['name'] = attribute.name
            context['values'] = '<BR ALIGN="LEFT"/>'.join(attribute.refers_to)

            rows.append(resource_attribute_row_view.format(**context))

        return "\n".join(rows)

    def __render_subgraph(self, label, element_type, elements):
        if not elements:
            return ''

        context = default_values.copy()
        context['label'] = label
        context['element_type'] = element_type
        context['elements'] = "|".join(elements)

        return subgraph_template.format(**context)

    def __render_edges(self):
        tmpl = "    {source} -> {dest}"
        edge_renderings = [tmpl.format(source=edge.source, dest=edge.dest)
                           for edge in self.model.resource_edges]
        return "\n".join(edge_renderings)
