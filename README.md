# cfnviz
Cloudformation template visualization using GraphViz

## Installation
`pip install cfnviz`

## Usage
### cfnviz
```
usage: cfnviz [-h] [-i INPUT_FILE] [-o OUTPUT_FILE]

a tool for visualizing cloudformation templates using graphviz. This will
generate a PNG temp (by default) file as output and open/xdg-open it. This is
useful for visualizing the current structure of the template at any given
time.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input FILE INPUT_FILE
                        The input template
  -o OUTPUT_FILE, --output FILE OUTPUT_FILE
                        The output dot file
```

### cfndot
```
usage: cfnviz [-h] [-i INPUT_FILE] [-o OUTPUT_FILE]

a tool for generating GraphViz diagrams (in dot file syntax) from AWS
CloudFormation templates.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input FILE INPUT_FILE
                        The input template
  -o OUTPUT_FILE, --output FILE OUTPUT_FILE
                        The output dot file
```
