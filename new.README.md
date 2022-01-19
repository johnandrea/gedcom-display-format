# gedcom-display-format
Convert a GEDCOM file to a format for display in network visualization.

The display may be of limited value for large trees as it takes a long time to arrange into a useful structure.

## Display ##

Output files can be used in display tools such as:
- Cytoscape: https://cytoscape.org
- GraphViz: https://graphviz.org

## Options ##

--format= graphml, dot, json
--include= all, ancestors, descendents, branch
--personid= <id value>
--iditem=  xref or user specified such as EXID, REFNUM, etc.

## Usage ##

```
gedcom-display-format.py gedcom-filename > formatted-file
```

## Formats ##

GraphML: http://graphml.graphdrawing.org
DOT: https://graphviz.org/doc/info/lang.html
JSON: https://www.w3schools.com/js/js_json_intro.asp
JS: see below

## Making Javascript format ##

A Javascript file, for insertion into an html page (etc.) with the use of a src= tag,
  can be created by making a JSON output file then prepending variable= and appending a semicolon (;).

## Installation ##

- Requires python 3.6+
- Copy Python file and supporting style file(s).
- also requires gedcom library [readgedcom.py](https://github.com/johnandrea/readgedcom)
