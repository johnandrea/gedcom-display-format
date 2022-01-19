# gedcom-display-format
Convert a GEDCOM file to a format for display in network visualization.

The display may be of limited value for large trees as it takes a long time to arrange into a useful structure.

## Display ##

Output files can be used in display tools such as:
- Cytoscape: https://cytoscape.org
- GraphViz: https://graphviz.org

## Options ##

--format= graphml or dot 

Type of output file produced. Default is graphml

--include= all, ancestors, descendents, branch

Which people to include in the output. Default is all
If choosing anything except "all", the personid option is required to select a person.

--personid= <id value>
  
The id of the person to select for output. Used in combination with the iditem option.
By default this is the the individual xref in the gedcom file and so may be given as for example
as @i42@ or I42 or just 42.

--iditem=  xref or user specified such as EXID, REFNUM, etc.
  
The tag in the gedcom file used to match the specified person. Default is xref which is the gedcom individual identifier.
  When using a non-xref tag, the given personid value must match exactly the value in the gedcom file.


## Usage ##

Minimal usage
```
gedcom-display-format.py gedcom-filename > file.graphml
```
Producing a file for Graphviz
```
gedcom-display-format.py --format=dot gedcom-filename > file.dot
# then making an image
dot -Tpng file.dot -o file.png
# or an svg for in-browser
dot -Tsvg file.dot -o file.svg
```
Output of the branch containing person with GEDCOM XREF @I15@
```
gedcom-display-format.py --include=branch --personid=15 gedcom-filename > file.graphml
```
The ancestors of person with EXID of 432
```
gedcom-display-format.py --format=dot --include=anc --personid=432 --iditem=exid gedcom-filename > file.dot
```

## Output Formats ##

GraphML: http://graphml.graphdrawing.org

DOT: https://graphviz.org/doc/info/lang.html

## Installation ##

- Requires python 3.6+
- Copy Python file and supporting style file(s).
- also requires gedcom library [readgedcom.py](https://github.com/johnandrea/readgedcom)
